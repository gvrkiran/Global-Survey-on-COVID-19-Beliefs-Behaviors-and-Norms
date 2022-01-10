## Scripts and data for replicating the figures for the paper "Global survey on COVID-19 beliefs, behaviors, and norms"

These scripts take the raw data (shared with users who signed the agreement with MIT and Facebook on Dropbox) and produce intermediate files that are used in the python notebook for the visualization

Some of the scripts make use of the API we developed for processing the data
https://covidsurvey.mit.edu/api.html

The following scripts are responsible for generating the respective data files:

1. code/getProcessedData.py
	> data/processed_data.txt.gz

2. code/getVaccineData.py
	> data/vaccine_accept_timeseries_weighted_bootstrap_mean.txt
	> data/vaccine_accept_timeseries_weighted_bootstrap_sem.txt
	> data/vaccine_norms_timeseries_bootstrap_mean.txt
	> data/vaccine_norms_timeseries_bootstrap_sem.txt
	> data/vaccine_accept_stacked_area.csv
	> data/demographic_data.csv
	> data/mismatch_index_raw_data.txt

3. code/getDataFromAPI.py
	> data/vaccine_accept_vaccine_norms_waves_and_snapshot.txt 
	> data/news_sources_mediums_consume_trust.txt
	> data/sample_size_timeseries.txt
	> data/effective_sample_size_timeseries.txt

4. data/survey_conversion_timeseries.txt - obtained from Facebook

5. data/india_state_codes.csv,data/us_state_population_fips.csv,data/waves_snapshot_countries.txt - general survey related files

6. code/misc_plots.py -- used to generate miscellaneous plots such as the weighted/unweighted gender ratio (in Appendix A), and the table containing the langauge information
	> makes use of the code code/make_numeric_dataset.py first to produce the file covid_survey_responses_numeric.txt.gz
# Generating the figures

With the data in place in the data/ folder, all the figures are produced by running the jupyter notebook
NHB Resource paper replication materials.ipynb
