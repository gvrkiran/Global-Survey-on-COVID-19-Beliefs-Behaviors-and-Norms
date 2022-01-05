## scripts

These scripts take the raw data (shared with users who signed the agreement with MIT and Facebook on Dropbox) and produce intermediate files that are used in the python notebook for the visualization

Some of the scripts make use of the API we developed for processing the data
https://covidsurvey.mit.edu/api.html

The following scripts are responsible for generating the respective data files:
scripts/getProcessedData.py
	- data/processed_data.txt.gz

scripts/getVaccineData.py
	- data/vaccine_accept_timeseries_weighted_bootstrap_mean.txt
	- data/vaccine_accept_timeseries_weighted_bootstrap_sem.txt
	- data/vaccine_norms_timeseries_bootstrap_mean.txt
	- data/vaccine_norms_timeseries_bootstrap_sem.txt
	- data/vaccine_accept_stacked_area.csv
	- data/demographic_data.csv
	- data/mismatch_index_raw_data.txt

scripts/getDataFromAPI.py
	- data/vaccine_accept_vaccine_norms_waves_and_snapshot.txt 
	- data/news_sources_mediums_consume_trust.txt
	- data/sample_size_timeseries.txt
	- data/effective_sample_size_timeseries.txt

survey_conversion_timeseries.txt - obtained from Facebook
india_state_codes.csv,us_state_population_fips.csv,waves_snapshot_countries.txt - general survey related files

# Generating the figures

With the data in place in the data/ folder, all the figures are produced by running the jupyter notebook
NHB Resource paper replication materials.ipynb
