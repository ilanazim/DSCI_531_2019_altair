'''
US Job Counts by Industry, 2006-2015
===============================
Interactive heat map shows how total US job change compared to
job change by industry surrounding stock crash in 2008.
'''


import pandas as pd
import altair as alt
from datetime import datetime as dt

us_employment = pd.read_csv("https://raw.githubusercontent.com/vega/vega-datasets/master/data/us-employment.csv")
us_employment["date"] = pd.to_datetime(us_employment["month"]) # date convert to datetime format and create properly named "date" column
us_employment = us_employment.drop(columns = ["month", "nonfarm_change"]) #drop nonfarm_change - I will recreate for all job types
us_employment = us_employment.rename(index=str, columns={"nonfarm": "all_jobs"})
us_employment = us_employment.melt(id_vars = ["date"], value_vars = list(us_employment.columns[0:22]), var_name = "job_type", value_name = "job_count").reset_index()

# create a change by job column to analyze change in specific job markets
monthly_change_by_job = []
for i in range(len(us_employment)-1):
    monthly_change_by_job.append(us_employment.job_count[i+1] - us_employment.job_count[i])
monthly_change_by_job.append(None) #add single value to list of 359 values to add to df
us_employment["monthly_change_by_job"] = monthly_change_by_job

# drop the 2015-12-01 rows to work with my monthly change column
date_drop = pd.to_datetime("2015-12-01")
us_employment = us_employment[us_employment.date != date_drop]

## Replace "_" so that job_types look nice on heat map!
us_employment.job_type = us_employment.job_type.str.replace("_", " ")

#interactive heatmap and barplot, concatonated

brush = alt.selection_interval(encodings=['x'])
opacity = alt.condition(brush, alt.value(0.9), alt.value(0.1))


plot_all_jobs = alt.Chart(pd.DataFrame(us_employment[us_employment.job_type == "all jobs"])).mark_bar().encode(
    alt.X("date:T", title = "Date"),
    alt.Y("monthly_change_by_job:Q", title = "Monthly Change in Jobs (thousands)"),
    alt.Color("monthly_change_by_job:Q", scale=alt.Scale(scheme='yellowgreenblue')
    ), opacity = opacity, tooltip=['date', 'monthly_change_by_job']).add_selection(
    brush).properties(
    title='Change in Total US Employment From 2006 to 2016', height = 200, width = 600)

jobs_heat_map = alt.Chart(us_employment[~us_employment.job_type.isin(["all jobs monthly change", "all jobs"])]).mark_rect().encode(
    alt.X('date:O', title = "Date", timeUnit='utcyearmonth', axis=alt.Axis(tickCount = 5)),
    alt.Y('job_type:N', title = "Job Type"),
    color = alt.Color('monthly_change_by_job:Q', legend=alt.Legend(title="Job Count Change in Thousands", orient = "right")),
    tooltip=['job_type','date', 'monthly_change_by_job'], opacity = opacity
).properties(title = "Heat Map US Jobs Over Time", width = 600, height = 450)

plot_all_jobs & jobs_heat_map