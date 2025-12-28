import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from app.clustering import get_zoom_tier, should_cluster, cluster_events

# Import config - handle both direct execution and Flask app context
Config = None
try:
    from config import Config
except ImportError:
    # If running as module, add parent to path
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from config import Config
    except ImportError:
        # Create a minimal Config if import fails
        class Config:
            RECENT_MIN_YEAR = 1678
            RECENT_MAX_YEAR = 2262
            CATEGORY_ORDER = ["era", "migration", "civilization", "empire", "war", "religion", "biblical"]
            TIMELINE_DATA_FILE = "timeline_data_4.csv"

class TimelineGenerator:
    """Generates timeline visualizations from database"""
    
    def __init__(self, db_session=None):
        """Initialize with database session"""
        self.db_session = db_session
        self.df = None
        try:
            self.RECENT_MIN_YEAR = Config.RECENT_MIN_YEAR
            self.RECENT_MAX_YEAR = Config.RECENT_MAX_YEAR
        except (NameError, AttributeError):
            # Fallback values if Config is not available
            self.RECENT_MIN_YEAR = 1678
            self.RECENT_MAX_YEAR = 2262
        self._load_data()
        
    def _load_data(self):
        """Load and prepare data from database"""
        # Store original dataframe for reference
        self._original_df = None
        if self.db_session is None:
            # Fallback: try to load from CSV if database not available
            try:
                csv_path = Config.TIMELINE_DATA_FILE
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    df = df.dropna(axis=1, how='all')
                else:
                    df = pd.DataFrame()
            except Exception as e:
                print(f"Error loading CSV fallback: {e}")
                df = pd.DataFrame()
        else:
            # Load from database
            from app.models import TimelineEvent
            events = self.db_session.query(TimelineEvent).all()
            
            if not events:
                df = pd.DataFrame()
            else:
                # Convert to list of dicts
                data = [event.to_dict() for event in events]
                df = pd.DataFrame(data)
                
                # Store original for reference
                self._original_df = df.copy()
                
                # Debug: log data loading
                print(f"DEBUG: Loaded {len(df)} events from database")
                if not df.empty:
                    print(f"DEBUG: Columns: {list(df.columns)}")
                    print(f"DEBUG: Sample start_year: {df['start_year'].head(3).tolist() if 'start_year' in df.columns else 'N/A'}")
        
        if df.empty:
            # Return empty dataframe with expected columns
            df = pd.DataFrame(columns=['id', 'title', 'category', 'continent', 'start_year', 'end_year', 'description', 'start_date', 'end_date'])
        
        # Ensure year columns exist and are numeric
        if not df.empty:
            if 'start_year' in df.columns:
                df["start_year"] = pd.to_numeric(df["start_year"], errors='coerce')
            else:
                df["start_year"] = None
                
            if 'end_year' in df.columns:
                df["end_year"] = pd.to_numeric(df["end_year"], errors='coerce')
            else:
                df["end_year"] = None
            
            # Convenience column for numeric plotting
            df["year"] = df["start_year"]
        else:
            # Empty dataframe - set default columns
            df["start_year"] = None
            df["end_year"] = None
            df["year"] = None
        
        # Parse dates where possible; out-of-range or invalid => NaT
        if "start_date" in df.columns:
            df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
        else:
            df["start_date"] = pd.NaT
            
        if "end_date" in df.columns:
            df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
        else:
            df["end_date"] = pd.NaT
        
        # Category order - include all categories found in data, not just predefined ones
        if "category" in df.columns and not df.empty:
            try:
                # Get all unique categories from the data
                data_categories = df["category"].dropna().unique().tolist()
                # Combine with predefined order, keeping order but adding any missing categories
                category_order = getattr(Config, 'CATEGORY_ORDER', ["era", "migration", "civilization", "empire", "war", "religion", "biblical"])
                all_categories = [cat for cat in category_order if cat in data_categories]
                # Add any categories in data that aren't in the predefined order
                for cat in data_categories:
                    if cat not in all_categories:
                        all_categories.append(cat)
                # Set as categorical with all categories
                df["category"] = pd.Categorical(df["category"], categories=all_categories, ordered=True)
            except Exception as e:
                print(f"Error setting category order: {e}")
                # If categorical fails, just keep as string
                pass
        
        self.df = df
    
    def get_filtered_data(self, start_year, end_year):
        """Get filtered data for the given year range"""
        if self.df.empty or 'start_year' not in self.df.columns or 'end_year' not in self.df.columns:
            return pd.DataFrame()
        
        # Handle NaN values in year columns
        mask = (
            (self.df["end_year"].notna()) & 
            (self.df["start_year"].notna()) &
            (self.df["end_year"] >= start_year) & 
            (self.df["start_year"] <= end_year)
        )
        return self.df[mask].copy()
    
    def make_figure_json(self, start_year, end_year, enable_clustering=True):
        """
        Build a dual-view timeline and return as JSON:
          - Row 1: numeric year axis (full deep-time range).
          - Row 2: real calendar dates for events that have valid start_date/end_date.
        
        Args:
            start_year: Start of visible time range
            end_year: End of visible time range
            enable_clustering: Whether to cluster events when zoomed out (default: True)
        """
        # Filter by overlap in numeric years
        df_filtered = self.get_filtered_data(start_year, end_year)
        
        # Debug: log how many events we have
        print(f"DEBUG: Total events in dataset: {len(self.df)}")
        print(f"DEBUG: Events in filtered range ({start_year} to {end_year}): {len(df_filtered)}")
        
        # Determine zoom tier and apply clustering if needed
        time_range = end_year - start_year
        tier = get_zoom_tier(time_range)
        cluster_info = {}
        
        if enable_clustering and not df_filtered.empty:
            should_cluster_events = should_cluster(tier, len(df_filtered), time_range)
            if should_cluster_events:
                print(f"DEBUG: Clustering enabled for tier {tier} (range: {time_range:,} years)")
                df_filtered, cluster_info = cluster_events(df_filtered, start_year, end_year, tier, enable_clustering)
                print(f"DEBUG: After clustering: {len(df_filtered)} markers (clusters + individual events)")
            else:
                print(f"DEBUG: Clustering not needed (tier {tier}, {len(df_filtered)} events)")
        
        # Check if we have data
        if df_filtered.empty:
            # Return empty figure with message
            fig = make_subplots(
                rows=1,
                cols=1,
                subplot_titles=(f"No data found for range {start_year:,} to {end_year:,}",)
            )
            fig.add_annotation(
                text="No events found in this time range. Try adjusting the year range.",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                template="plotly_dark", 
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            fig_json = json.loads(fig.to_json())
            if '_metadata' not in fig_json:
                fig_json['_metadata'] = {}
            fig_json['_metadata']['cluster_info'] = cluster_info
            return fig_json
        
        # --- Subplot layout: 2 rows, shared categories on y ---
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_yaxes=True,
            row_heights=[0.6, 0.4],
            vertical_spacing=0.12,
            subplot_titles=('', ''),  # No titles to avoid overlap
        )
        
        # -------------------
        # Row 1: numeric years
        # -------------------
        # Ensure 'year' column exists (needed for plotting)
        if 'year' not in df_filtered.columns:
            df_filtered['year'] = df_filtered.apply(
                lambda row: (row['start_year'] + row['end_year']) / 2 if pd.notna(row.get('end_year')) and row['end_year'] != row['start_year'] else row['start_year'],
                axis=1
            )
        
        # Remove rows with missing year data
        df_plot = df_filtered.dropna(subset=['year']).copy()
        
        print(f"DEBUG: Events after dropping NaN years: {len(df_plot)}")
        
        # Handle missing categories - convert to string first to avoid Categorical issues
        if 'category' in df_plot.columns:
            # Convert categorical to string to avoid issues with adding new categories
            if pd.api.types.is_categorical_dtype(df_plot['category']):
                df_plot['category'] = df_plot['category'].astype(str)
            # Fill any NaN values (which are now 'nan' strings) with a default
            df_plot['category'] = df_plot['category'].replace('nan', 'other').fillna('other')
        
        print(f"DEBUG: Final events to plot: {len(df_plot)}")
        print(f"DEBUG: Categories in plot: {df_plot['category'].value_counts().to_dict()}")
        
        if df_plot.empty:
            # If no valid data after dropping NaN, return empty figure
            fig = make_subplots(
                rows=1,
                cols=1,
                subplot_titles=(f"No valid data for range {start_year:,} to {end_year:,}",)
            )
            fig.add_annotation(
                text="Data found but missing required fields (year).",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                template="plotly_dark", 
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            fig_json = json.loads(fig.to_json())
            if '_metadata' not in fig_json:
                fig_json['_metadata'] = {}
            fig_json['_metadata']['cluster_info'] = cluster_info
            return fig_json
        
        # Create scatter plot manually to ensure ALL data points are included
        # Group by category to create separate traces with proper colors
        # Get unique categories and assign colors
        categories = df_plot['category'].unique()
        colors = px.colors.qualitative.Set3  # Use a color palette
        
        # Create a trace for each category to ensure all points are included
        for idx, cat in enumerate(categories):
            cat_data = df_plot[df_plot['category'] == cat]
            
            # Prepare hover text and customdata for each point
            hover_templates = []
            customdata_list = []
            
            for _, row in cat_data.iterrows():
                # Check if this is a cluster
                is_cluster = row.get('is_cluster', False)
                
                # Hover text
                if is_cluster:
                    # Cluster hover shows count and category
                    event_count = row.get('title', '').replace(' events', '').replace('events', '').strip()
                    parts = [f"<b>Cluster: {row.get('title', 'N/A')}</b>"]
                    parts.append(f"Category: {row.get('category', 'N/A')}")
                    parts.append(f"Time: {int(row.get('start_year', 0)):,} - {int(row.get('end_year', 0)):,}")
                    parts.append("<br><i>Click to expand and view events</i>")
                else:
                    parts = [f"<b>{row.get('title', 'N/A')}</b>"]
                    if pd.notna(row.get('start_year')):
                        parts.append(f"Start: {int(row['start_year']):,}")
                    if pd.notna(row.get('end_year')) and row.get('end_year') != row.get('start_year'):
                        parts.append(f"End: {int(row['end_year']):,}")
                    if pd.notna(row.get('continent')):
                        parts.append(f"Continent: {row['continent']}")
                    if pd.notna(row.get('description')):
                        desc = str(row['description'])[:150]  # Limit description length
                        if len(str(row['description'])) > 150:
                            desc += "..."
                        parts.append(f"<br><i>{desc}</i>")
                hover_templates.append("<br>".join(parts))
                
                # Customdata for click events: [id, title, category, continent, start_year, end_year, start_date, end_date, description, lat, lon, location_label, geometry, location_confidence]
                start_date_str = None
                end_date_str = None
                if pd.notna(row.get('start_date')):
                    try:
                        start_date_str = row['start_date'].strftime('%Y-%m-%d') if hasattr(row['start_date'], 'strftime') else str(row['start_date'])
                    except:
                        start_date_str = None
                if pd.notna(row.get('end_date')):
                    try:
                        end_date_str = row['end_date'].strftime('%Y-%m-%d') if hasattr(row['end_date'], 'strftime') else str(row['end_date'])
                    except:
                        end_date_str = None
                
                # Get location fields
                lat = row.get('lat') if pd.notna(row.get('lat')) else None
                lon = row.get('lon') if pd.notna(row.get('lon')) else None
                location_label = str(row.get('location_label', '')) if pd.notna(row.get('location_label')) else None
                geometry = str(row.get('geometry', '')) if pd.notna(row.get('geometry')) else None
                location_confidence = str(row.get('location_confidence', 'exact')) if pd.notna(row.get('location_confidence')) else 'exact'
                
                # Check if this is a cluster
                is_cluster = row.get('is_cluster', False)
                cluster_id = row.get('cluster_id', None)
                
                customdata_list.append([
                    str(row.get('id', '')),
                    str(row.get('title', 'Unknown')),
                    str(row.get('category', 'N/A')),
                    str(row.get('continent', 'N/A')),
                    int(row['start_year']) if pd.notna(row.get('start_year')) else None,
                    int(row['end_year']) if pd.notna(row.get('end_year')) else None,
                    start_date_str,
                    end_date_str,
                    str(row.get('description', '')) if pd.notna(row.get('description')) else '',
                    float(lat) if lat is not None else None,
                    float(lon) if lon is not None else None,
                    location_label,
                    geometry,
                    location_confidence,
                    is_cluster,
                    cluster_id
                ])
            
            # Separate clusters from individual events for different styling
            cluster_mask = cat_data.get('is_cluster', pd.Series([False] * len(cat_data)))
            individual_data = cat_data[~cluster_mask] if 'is_cluster' in cat_data.columns else cat_data
            cluster_data = cat_data[cluster_mask] if 'is_cluster' in cat_data.columns else pd.DataFrame()
            
            # Create trace for individual events
            if not individual_data.empty:
                individual_indices = [i for i, is_clust in enumerate(cluster_mask) if not is_clust] if 'is_cluster' in cat_data.columns else list(range(len(cat_data)))
                individual_hover = [hover_templates[i] for i in individual_indices]
                individual_customdata = [customdata_list[i] for i in individual_indices]
                
                trace = go.Scatter(
                    x=individual_data['year'].tolist(),
                    y=[str(cat)] * len(individual_data),
                    mode='markers',
                    name=str(cat),
                    marker=dict(
                        size=10,
                        color=colors[idx % len(colors)],
                        line=dict(width=1, color="rgba(255, 255, 255, 0.3)"),
                        opacity=0.85
                    ),
                    text=individual_hover,
                    customdata=individual_customdata,
                    hovertemplate='%{text}<br>Year: %{x:,}<extra></extra>',
                )
                fig.add_trace(trace, row=1, col=1)
            
            # Create trace for clusters (larger, different style)
            if not cluster_data.empty:
                cluster_indices = [i for i, is_clust in enumerate(cluster_mask) if is_clust]
                cluster_hover = [hover_templates[i] for i in cluster_indices]
                cluster_customdata = [customdata_list[i] for i in cluster_indices]
                
                cluster_trace = go.Scatter(
                    x=cluster_data['year'].tolist(),
                    y=[str(cat)] * len(cluster_data),
                    mode='markers',
                    name=f"{cat} (clusters)",
                    marker=dict(
                        size=16,
                        color=colors[idx % len(colors)],
                        line=dict(width=2, color="rgba(255, 215, 0, 0.8)"),
                        opacity=0.9,
                        symbol='diamond'
                    ),
                    text=cluster_hover,
                    customdata=cluster_customdata,
                    hovertemplate='%{text}<br>Year: %{x:,}<br><i>Click to expand cluster</i><extra></extra>',
                )
                fig.add_trace(cluster_trace, row=1, col=1)
        
        print(f"DEBUG: Number of traces added: {len(categories)}")
        print(f"DEBUG: Total data points: {len(df_plot)}")
        print(f"DEBUG: Points per category: {df_plot.groupby('category').size().to_dict()}")
        
        # Top x-axis: SHOW tick labels, move them to top
        fig.update_xaxes(
            range=[start_year, end_year],
            title_text="",  # Removed title to avoid overlap
            showgrid=True,
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor="rgba(255, 255, 255, 0.2)",
            type="linear",
            showticklabels=True,
            side="top",
            tickangle=0,
            automargin=True,
            row=1,
            col=1,
        )
        
        fig.update_yaxes(
            title_text="Category",
            autorange="reversed",
            row=1,
            col=1,
        )
        
        # -------------------
        # Row 2: real dates (recent)
        # -------------------
        df_recent = df_filtered[
            (df_filtered["start_date"].notna()) &
            (df_filtered["start_date"].dt.year >= self.RECENT_MIN_YEAR) &
            (df_filtered["start_date"].dt.year <= self.RECENT_MAX_YEAR)
        ].copy()
        
        if not df_recent.empty:
            fig_dates = px.scatter(
                df_recent,
                x="start_date",
                y="category",
                color="category",
                hover_name="title",
                hover_data={
                    "start_date": True,
                    "end_date": True,
                    "start_year": True,
                    "end_year": True,
                    "continent": True,
                    "description": True,
                    "category": False,
                },
            )
            
            for trace in fig_dates.data:
                trace.showlegend = False  # legend already shown from top plot
                trace.marker.update(size=10, line=dict(width=1, color="rgba(255, 255, 255, 0.3)"))
                # Add customdata to date traces as well
                if hasattr(trace, 'customdata') and trace.customdata:
                    # Keep existing customdata if present
                    pass
                else:
                    # Create customdata from the dataframe
                    trace_customdata = []
                    for _, row in df_recent.iterrows():
                        start_date_str = None
                        end_date_str = None
                        if pd.notna(row.get('start_date')):
                            try:
                                start_date_str = row['start_date'].strftime('%Y-%m-%d') if hasattr(row['start_date'], 'strftime') else str(row['start_date'])
                            except:
                                start_date_str = None
                        if pd.notna(row.get('end_date')):
                            try:
                                end_date_str = row['end_date'].strftime('%Y-%m-%d') if hasattr(row['end_date'], 'strftime') else str(row['end_date'])
                            except:
                                end_date_str = None
                        
                        # Get location fields
                        lat = row.get('lat') if pd.notna(row.get('lat')) else None
                        lon = row.get('lon') if pd.notna(row.get('lon')) else None
                        location_label = str(row.get('location_label', '')) if pd.notna(row.get('location_label')) else None
                        geometry = str(row.get('geometry', '')) if pd.notna(row.get('geometry')) else None
                        location_confidence = str(row.get('location_confidence', 'exact')) if pd.notna(row.get('location_confidence')) else 'exact'
                        
                        # Check if this is a cluster (date traces typically won't have clusters, but check anyway)
                        is_cluster = row.get('is_cluster', False)
                        cluster_id = row.get('cluster_id', None)
                        
                        trace_customdata.append([
                            str(row.get('id', '')),
                            str(row.get('title', 'Unknown')),
                            str(row.get('category', 'N/A')),
                            str(row.get('continent', 'N/A')),
                            int(row['start_year']) if pd.notna(row.get('start_year')) else None,
                            int(row['end_year']) if pd.notna(row.get('end_year')) else None,
                            start_date_str,
                            end_date_str,
                            str(row.get('description', '')) if pd.notna(row.get('description')) else '',
                            float(lat) if lat is not None else None,
                            float(lon) if lon is not None else None,
                            location_label,
                            geometry,
                            location_confidence,
                            is_cluster,
                            cluster_id
                        ])
                    trace.customdata = trace_customdata
                fig.add_trace(trace, row=2, col=1)
            
            # Set date-axis range based on requested year window & what's available
            min_recent_year = max(start_year, self.RECENT_MIN_YEAR)
            max_recent_year = min(
                end_year,
                int(df_recent["start_date"].dt.year.max()) if not df_recent.empty else end_year
            )
            
            if min_recent_year <= max_recent_year:
                recent_start = pd.to_datetime(f"{min_recent_year}-01-01")
                recent_end = pd.to_datetime(f"{max_recent_year}-12-31")
            else:
                recent_start = df_recent["start_date"].min()
                recent_end = df_recent["start_date"].max()
            
            fig.update_xaxes(
                range=[recent_start, recent_end],
                title_text="",  # Removed title to avoid overlap
                showgrid=True,
                zeroline=True,
                zerolinewidth=1,
                zerolinecolor="rgba(255, 255, 255, 0.2)",
                type="date",
                tickangle=-30,
                automargin=True,
                row=2,
                col=1,
            )
        else:
            # No precise dates in this window
            fig.update_xaxes(
                title_text="",  # Removed title
                tickangle=-30,
                automargin=True,
                row=2,
                col=1,
            )
        
        # Hide duplicate category labels on lower y-axis
        fig.update_yaxes(showticklabels=False, row=2, col=1)
        
        # Store cluster info in layout for frontend access
        fig.update_layout(
            template="plotly_dark",
            height=900,
            hovermode="closest",
            dragmode="pan",
            legend_title_text="Category",
            title_text="",  # Removed title to avoid overlap
            margin=dict(t=40, b=80, l=60, r=40),  # Reduced top margin since no title
            # Observatory Mode: Transparent backgrounds
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family="'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                size=12,
                color='rgba(255, 255, 255, 0.9)'
            ),
            hoverlabel=dict(
                bgcolor='rgba(0, 0, 0, 0.8)',
                bordercolor='rgba(255, 255, 255, 0.3)',
                font_size=13
            )
        )
        
        # Update axes for Observatory Mode styling
        fig.update_xaxes(
            gridcolor='rgba(255, 255, 255, 0.1)',
            zerolinecolor='rgba(255, 255, 255, 0.2)',
            showline=False,
            row=1, col=1
        )
        fig.update_xaxes(
            gridcolor='rgba(255, 255, 255, 0.1)',
            zerolinecolor='rgba(255, 255, 255, 0.2)',
            showline=False,
            row=2, col=1
        )
        fig.update_yaxes(
            gridcolor='rgba(255, 255, 255, 0.05)',
            showline=False,
            row=1, col=1
        )
        fig.update_yaxes(
            gridcolor='rgba(255, 255, 255, 0.05)',
            showline=False,
            row=2, col=1
        )
        
        # Convert to JSON and add cluster info to metadata
        fig_json = json.loads(fig.to_json())
        if '_metadata' not in fig_json:
            fig_json['_metadata'] = {}
        fig_json['_metadata']['cluster_info'] = cluster_info
        return fig_json
    
    def reload_data(self):
        """Reload data from database"""
        try:
            self._load_data()
            return True
        except Exception as e:
            print(f"Error reloading data: {e}")
            import traceback
            traceback.print_exc()
            return False

