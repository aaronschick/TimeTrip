import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os

# Import config - handle both direct execution and Flask app context
try:
    from config import Config
except ImportError:
    # If running as module, add parent to path
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import Config

class TimelineGenerator:
    """Generates timeline visualizations from CSV data"""
    
    def __init__(self, csv_path):
        """Initialize with path to CSV data file"""
        self.csv_path = csv_path
        self.df = self._load_data(csv_path)
        self.RECENT_MIN_YEAR = Config.RECENT_MIN_YEAR
        self.RECENT_MAX_YEAR = Config.RECENT_MAX_YEAR
        
    def _load_data(self, csv_path):
        """Load and prepare data from CSV"""
        # Read CSV and drop any empty columns (from trailing commas)
        df = pd.read_csv(csv_path)
        df = df.dropna(axis=1, how='all')  # Remove completely empty columns
        
        # Ensure year columns exist and are numeric
        df["start_year"] = pd.to_numeric(df["start_year"], errors='coerce')
        df["end_year"] = pd.to_numeric(df["end_year"], errors='coerce')
        
        # Convenience column for numeric plotting
        df["year"] = df["start_year"]
        
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
        if "category" in df.columns:
            # Get all unique categories from the data
            data_categories = df["category"].dropna().unique().tolist()
            # Combine with predefined order, keeping order but adding any missing categories
            all_categories = [cat for cat in Config.CATEGORY_ORDER if cat in data_categories]
            # Add any categories in data that aren't in the predefined order
            for cat in data_categories:
                if cat not in all_categories:
                    all_categories.append(cat)
            # Set as categorical with all categories
            df["category"] = pd.Categorical(df["category"], categories=all_categories, ordered=True)
        
        return df
    
    def get_filtered_data(self, start_year, end_year):
        """Get filtered data for the given year range"""
        mask = (self.df["end_year"] >= start_year) & (self.df["start_year"] <= end_year)
        return self.df[mask].copy()
    
    def make_figure_json(self, start_year, end_year):
        """
        Build a dual-view timeline and return as JSON:
          - Row 1: numeric year axis (full deep-time range).
          - Row 2: real calendar dates for events that have valid start_date/end_date.
        """
        # Filter by overlap in numeric years
        df_filtered = self.get_filtered_data(start_year, end_year)
        
        # Debug: log how many events we have
        print(f"DEBUG: Total events in dataset: {len(self.df)}")
        print(f"DEBUG: Events in filtered range ({start_year} to {end_year}): {len(df_filtered)}")
        
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
            fig.update_layout(template="plotly_dark", height=400)
            return json.loads(fig.to_json())
        
        # --- Subplot layout: 2 rows, shared categories on y ---
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_yaxes=True,
            row_heights=[0.6, 0.4],
            vertical_spacing=0.12,
            subplot_titles=(
                f"Numeric Year Timeline ({start_year:,} to {end_year:,})",
                "Recent History (Calendar Dates)",
            ),
        )
        
        # -------------------
        # Row 1: numeric years
        # -------------------
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
            fig.update_layout(template="plotly_dark", height=400)
            return json.loads(fig.to_json())
        
        # Create scatter plot manually to ensure ALL data points are included
        # Group by category to create separate traces with proper colors
        # Get unique categories and assign colors
        categories = df_plot['category'].unique()
        colors = px.colors.qualitative.Set3  # Use a color palette
        
        # Create a trace for each category to ensure all points are included
        for idx, cat in enumerate(categories):
            cat_data = df_plot[df_plot['category'] == cat]
            
            # Prepare hover text with all information for each point
            hover_templates = []
            for _, row in cat_data.iterrows():
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
            
            # Create trace with all points for this category
            trace = go.Scatter(
                x=cat_data['year'].tolist(),
                y=[str(cat)] * len(cat_data),  # All points at same y position (category)
                mode='markers',
                name=str(cat),
                marker=dict(
                    size=8,
                    color=colors[idx % len(colors)],
                    line=dict(width=1, color="black"),
                    opacity=0.8
                ),
                text=hover_templates,
                hovertemplate='%{text}<br>Year: %{x:,}<extra></extra>',
            )
            fig.add_trace(trace, row=1, col=1)
        
        print(f"DEBUG: Number of traces added: {len(categories)}")
        print(f"DEBUG: Total data points: {len(df_plot)}")
        print(f"DEBUG: Points per category: {df_plot.groupby('category').size().to_dict()}")
        
        # Top x-axis: SHOW tick labels, move them to top
        fig.update_xaxes(
            range=[start_year, end_year],
            title_text="Year (negative = BCE, very negative = deep time)",
            showgrid=True,
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="white",
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
                trace.marker.update(size=8, line=dict(width=1, color="black"))
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
                title_text="Calendar Date (recent events with precise dates)",
                showgrid=True,
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor="white",
                type="date",
                tickangle=-30,
                automargin=True,
                row=2,
                col=1,
            )
        else:
            # No precise dates in this window
            fig.update_xaxes(
                title_text="Calendar Date (no precise-dated events here)",
                tickangle=-30,
                automargin=True,
                row=2,
                col=1,
            )
        
        # Hide duplicate category labels on lower y-axis
        fig.update_yaxes(showticklabels=False, row=2, col=1)
        
        fig.update_layout(
            template="plotly_dark",
            height=900,
            hovermode="closest",
            dragmode="pan",
            legend_title_text="Category",
            title_text="World History Mega-Timeline (Years + Calendar Dates)",
            margin=dict(t=100, b=80, l=60, r=40),
        )
        
        # Convert to JSON for frontend
        return json.loads(fig.to_json())
    
    def save_data(self):
        """Save the current dataframe back to CSV file"""
        try:
            # Check if file is writable
            if os.path.exists(self.csv_path) and not os.access(self.csv_path, os.W_OK):
                # Try to use a writable location (for production environments like Render)
                # On Render, repo files are read-only, so we'd need a database for persistence
                # For now, try a temp location or return False with a helpful message
                print(f"Warning: CSV file is not writable at {self.csv_path}")
                print("Note: On production platforms like Render, files in the repo are read-only.")
                print("Changes will be lost on redeploy. Consider using a database for persistence.")
                # Try to write to a writable location as fallback
                import tempfile
                temp_dir = os.environ.get('TMPDIR', '/tmp')
                fallback_path = os.path.join(temp_dir, 'timeline_data.csv')
                print(f"Attempting to write to fallback location: {fallback_path}")
                self.csv_path = fallback_path
            
            # Prepare dataframe for saving - keep only original CSV columns
            columns_to_save = ['id', 'title', 'category', 'continent', 'start_year', 'end_year', 'description']
            
            # Add date columns if they exist in the dataframe
            if 'start_date' in self.df.columns:
                columns_to_save.append('start_date')
            if 'end_date' in self.df.columns:
                columns_to_save.append('end_date')
            
            # Select only columns that exist
            columns_to_save = [col for col in columns_to_save if col in self.df.columns]
            
            # Create a copy for saving
            df_to_save = self.df[columns_to_save].copy()
            
            # Convert date columns to strings if they exist
            if 'start_date' in df_to_save.columns:
                df_to_save['start_date'] = df_to_save['start_date'].apply(
                    lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and hasattr(x, 'strftime') else ''
                )
            if 'end_date' in df_to_save.columns:
                df_to_save['end_date'] = df_to_save['end_date'].apply(
                    lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and hasattr(x, 'strftime') else ''
                )
            
            # Fill NaN values with empty strings for CSV compatibility
            df_to_save = df_to_save.fillna('')
            
            # Save to CSV
            df_to_save.to_csv(self.csv_path, index=False)
            print(f"Data saved successfully to {self.csv_path}")
            return True
        except PermissionError as e:
            print(f"Permission error saving data: {e}")
            print("The CSV file may be read-only. On production platforms, consider using a database.")
            return False
        except Exception as e:
            print(f"Error saving data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def reload_data(self):
        """Reload data from CSV file"""
        try:
            self.df = self._load_data(self.csv_path)
            return True
        except Exception as e:
            print(f"Error reloading data: {e}")
            import traceback
            traceback.print_exc()
            return False

