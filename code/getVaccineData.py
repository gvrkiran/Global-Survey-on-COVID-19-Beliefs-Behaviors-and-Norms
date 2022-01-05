import sys;
import pandas as pd;
import numpy as np;
from scipy.spatial import distance;
from scipy import stats

f = open("../data/waves_snapshot_countries.txt");
lines = f.readlines();
dict_countries_mapping = {};

for line in lines:
    line = line.strip();
    line_split = line.split(",");
    if(line_split[2]=="waves"):
        dict_countries_mapping[line_split[0]] = 1;


def convertCountryToISO2(country_name):
    try:
        iso2_name = dict_countries[country_name];
        return iso2_name;
    except:
        #print(country_name)
        return "XX";
    
def convertWaveToString(wave_id):
    try:
        if(wave_id!=""):
            wave_id = "wave" + str(int(float(wave_id)));
    except:
        wave_id = "";
    return wave_id;

def getVaccineFracWeighted(data):
    data = data.dropna(subset=['vaccine_accept'])
    weighted = pd.Series(data[['vaccine_accept','weight_demo']].groupby('vaccine_accept').sum()['weight_demo'])/data['weight_demo'].sum();
    dict_weighted = weighted.to_dict();
    weighted = normalizeFractions(dict_weighted)
    unweighted = pd.Series(data[['vaccine_accept','placebo']].groupby('vaccine_accept').sum()['placebo'])/data['placebo'].sum();
    return {"vaccine_accept_weighted":weighted},{"vaccine_accept_unweighted":unweighted.round(3).to_dict()};

def getVaccineFracWeightedBootstrap(data):
    data = data.dropna(subset=['vaccine_accept'])
    x = []; y = [];
    for i in range(1,100):
        data_sample = data.sample(frac=0.3,replace=True);
        weighted = pd.Series(data_sample[['vaccine_accept','weight_demo']].groupby('vaccine_accept').sum()['weight_demo'])/data_sample['weight_demo'].sum();
        dict_weighted = weighted.to_dict();
#        weighted = normalizeFractions(dict_weighted)
        val = dict_weighted["I have already been vaccinated"] if "I have already been vaccinated" in dict_weighted else 0;
        x.append(dict_weighted["Yes"] + val);

    return np.mean(x),stats.sem(x);
#    return {"vaccine_accept_weighted":weighted};

def mergeAlreadyVaccinated(vaccine_accept):
    if(vaccine_accept=="I have already been vaccinated"):
        return "Yes"
    else:
        return vaccine_accept;

# remove the -1 and re-normalize the weights to sum to 1
def normalizeFractions(dict_weighted):
    dict_output = {};
    count = 0.0;
    for keys in dict_weighted:
        if(keys!="-1"):
            dict_output[keys] = round(dict_weighted[keys]/(1-dict_weighted['-1']),3);
    return dict_output;

data = pd.read_csv("../data/processed_data.txt.gz",sep="\t",compression='gzip');
data = data.dropna(subset=["weight_demo"]);
data["vaccine_accept"] = data["vaccine_accept"].apply(mergeAlreadyVaccinated);

data_demographics = data[["country","gender","age","education","weight_demo"]]
data_demographics.to_csv("../data/demographics_data.csv",sep="\t",index=False)

## uses data from questions "community_action_importance: How important is it for you to take actions to prevent the spread of COVID-19 in your community?
## and community_action_norms: How important do other people in your community think it is to take actions to prevent the spread of COVID-19?"
data_mismatch = data[["country","weight_demo","community_action_importance","community_action_norms"]]
data_mismatch.to_csv("../data/mismatch_index_raw_data.txt",sep=",",index=False)

## uses data from questions "vaccine_accept: If a vaccine for COVID-19 becomes available, would you choose to get vaccinated?"
## and "norms_vaccine: Out of 100 people in your community, how many do you think would take the COVID-19 vaccine if it were made available?"
out_weighted = open("../data/vaccine_accept_timeseries_weighted_bootstrap_mean.txt","w");
out_weighted_sem = open("../data/vaccine_accept_timeseries_weighted_bootstrap_sem.txt","w");

tmp_str = "country,";
for i in range(1,20):
    wave_param = "wave" + str(i);
    tmp_str += wave_param + ",";

out_weighted.write(tmp_str.strip(",") + "\n");
out_weighted_sem.write(tmp_str.strip(",") + "\n");

for country in dict_countries_mapping.keys():
    data_country = data[data.country.isin([country])];
    
    tmp_str_weighted = country + ",";
    tmp_str_weighted_sem = country + ",";
    tmp_str_unweighted = country + ",";
    for i in range(1,20):
        wave_param = "wave" + str(i);
        data_per_wave = data_country[data_country.wave.isin([wave_param])];
#        vaccine_data_weighted,vaccine_data_unweighted = getVaccineFracWeighted(data_per_wave);
        mean,sem = getVaccineFracWeightedBootstrap(data_per_wave);
#        tmp_str_weighted += str(vaccine_data_weighted["vaccine_accept_weighted"]["No"]) + ",";
#        tmp_str_unweighted += str(vaccine_data_unweighted["vaccine_accept_unweighted"]["No"]) + ",";
        tmp_str_weighted += str(mean) + ",";
        tmp_str_weighted_sem += str(sem) + ",";

    out_weighted.write(tmp_str_weighted.strip(",") + "\n");
    out_weighted_sem.write(tmp_str_weighted_sem.strip(",") + "\n");
#    out_unweighted.write(tmp_str_unweighted.strip(",") + "\n");

out_weighted.close();
out_weighted_sem.close();
#out_unweighted.close();


def getVaccineNormsWeighted(data):
    data = data.dropna(subset=['norms_vaccine'])
    data = data[data.norms_vaccine!=-1];
    norms_vaccine = (data["norms_vaccine"]*data["weight_demo"]).sum()/data["weight_demo"].sum();
    return {"norms_vaccine":{"weighted":norms_vaccine}};

def getVaccineNormsWeightedBootstrap(data):
    data = data.dropna(subset=['norms_vaccine'])
    x = []; y = [];
    for i in range(1,100):
        data_sample = data.sample(frac=0.3,replace=True);
        norms_vaccine = (data["norms_vaccine"]*data["weight_demo"]).sum()/data["weight_demo"].sum();
        x.append(norms_vaccine/100);

    return np.mean(x),stats.sem(x);
#

out_mismatch = open("../data/vaccine_norms_timeseries_bootstrap_mean.txt","w");
out_mismatch_sem = open("../data/vaccine_norms_timeseries_bootstrap_sem.txt","w");

tmp_str = "country,";
for i in range(9,20):
    wave_param = "wave" + str(i);
    tmp_str += wave_param + ",";

out_mismatch.write(tmp_str.strip(",") + "\n");
out_mismatch_sem.write(tmp_str.strip(",") + "\n");

for country in dict_countries_mapping.keys():
    data_country = data[data.country.isin([country])];
    
    tmp_str_weighted = country + ",";
    tmp_str_weighted_sem = country + ",";
    tmp_str_unweighted = country + ",";
    for i in range(9,20):
        wave_param = "wave" + str(i);
        data_per_wave = data_country[data_country.wave.isin([wave_param])];
#        vaccine_data_weighted,vaccine_data_unweighted = getVaccineFracWeighted(data_per_wave);
        mean,sem = getVaccineNormsWeightedBootstrap(data_per_wave);
        tmp_str_weighted += str(mean) + ",";
        tmp_str_weighted_sem += str(sem) + ",";

    out_mismatch.write(tmp_str_weighted.strip(",") + "\n");
    out_mismatch_sem.write(tmp_str_weighted_sem.strip(",") + "\n");

out_mismatch.close();
out_mismatch_sem.close();

out = open("../data/vaccine_accept_stacked_area.csv","w");
out.write("wave,country,Yes,Don't know,No\n");
dict_average = {};

for country in dict_countries_mapping.keys():
    data_country = data[data.country.isin([country])];
    
    tmp_str_weighted = country + ",";
    tmp_str_weighted_sem = country + ",";
    tmp_str_unweighted = country + ",";
    for i in range(1,20):
        wave_param = "wave" + str(i);
        data_per_wave = data_country[data_country.wave.isin([wave_param])];
        vaccine_data_weighted,vaccine_data_unweighted = getVaccineFracWeighted(data_per_wave);
        out.write(str(i) + "," + country + "," + str(vaccine_data_weighted["vaccine_accept_weighted"]["Yes"]) + "," +
                str(vaccine_data_weighted["vaccine_accept_weighted"]["Don't know"]) + "," + 
                str(vaccine_data_weighted["vaccine_accept_weighted"]["No"]) + "\n");
        if(i in dict_average):
            tmp = dict_average[i];
            tmp["Yes"] += vaccine_data_weighted["vaccine_accept_weighted"]["Yes"];
            tmp["No"] += vaccine_data_weighted["vaccine_accept_weighted"]["Don't know"];
            tmp["Don't know"] += vaccine_data_weighted["vaccine_accept_weighted"]["No"];
            dict_average[i] = tmp;
        else:
            tmp = {"Yes":0,"No":0,"Don't know":0};
            tmp["Yes"] += vaccine_data_weighted["vaccine_accept_weighted"]["Yes"];
            tmp["No"] += vaccine_data_weighted["vaccine_accept_weighted"]["Don't know"];
            tmp["Don't know"] += vaccine_data_weighted["vaccine_accept_weighted"]["No"];
            dict_average[i] = tmp;
#        mean,sem = getVaccineFracWeightedBootstrap(data_per_wave);
#        tmp_str_weighted += str(vaccine_data_weighted["vaccine_accept_weighted"]["No"]) + ",";
#        tmp_str_unweighted += str(vaccine_data_unweighted["vaccine_accept_unweighted"]["No"]) + ",";

for keys in dict_average.keys():
    out.write(str(keys) + ",average," + str(dict_average[keys]["Yes"]/len(dict_countries_mapping.keys())) + ","
            + str(dict_average[keys]["Don't know"]/len(dict_countries_mapping.keys())) + ","
            + str(dict_average[keys]["No"]/len(dict_countries_mapping.keys())) + "\n");

out.close();
