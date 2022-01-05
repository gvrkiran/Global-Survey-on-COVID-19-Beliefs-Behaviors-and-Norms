import pandas as pd;

f8 = open("../data/us_state_population_fips.csv");
lines8 = f8.readlines();
dict_us_state = {};

for line in lines8:
    line = line.strip();
    line_split = line.split(",");
    dict_us_state[line_split[1]] = line_split[2];

f9 = open("../data/india_state_codes.csv");
lines9 = f9.readlines();
dict_india_state = {};

for line in lines9:
    line = line.strip();
    line_split = line.split(",");
    dict_india_state[line_split[0]] = line_split[1];

f = open("../data/waves_snapshot_countries.txt");
lines = f.readlines();
dict_countries = {};
dict_country_params = {};
dict_waves_snapshot = {};

for line in lines:
    line = line.strip();
    line_split = line.split(",");
    dict_countries[line_split[1]] = line_split[0];
    dict_country_params[line_split[0]] = 1;
    wave_or_snapshot = line_split[2];
    if(wave_or_snapshot in dict_waves_snapshot):
        tmp = dict_waves_snapshot[wave_or_snapshot];
        tmp[line_split[0]] = 1;
        dict_waves_snapshot[wave_or_snapshot] = tmp;
    else:
        tmp = {};
        tmp[line_split[0]] = 1;
        dict_waves_snapshot[wave_or_snapshot] = tmp;


def convertCountryToISO2(country_name):
    try:
        iso2_name = dict_countries[country_name];
        return iso2_name;
    except:
        #print(country_name)
        return "XX";
    
def convertUSState(us_state):
    try:
        iso2_name = dict_us_state[us_state];
        return iso2_name;
    except:
        #print(us_state)
        return "";
    
def convertIndiaState(india_state):
    try:
        iso2_name = dict_india_state[india_state.strip()];
        return iso2_name;
    except:
        #print("India state", india_state)
        return "";

def convertWaveToString(wave_id):
    try:
        if(wave_id!=""):
            wave_id = "wave" + str(int(float(wave_id)));
    except:
        wave_id = "";
    return wave_id;

def processEducation(education):
    dict_education = {'College / university': 'college', 'Secondary school': 'secondary_school', 'Graduate school': 'graduate_school', 'Primary school': 'primary_school', 'Less than primary school': 'less_than_primary'};
    try:
        education_mapping = dict_education[education];
        return education_mapping;
    except:
        return "";

# change the path to the exact file containing the dataset
data = pd.read_csv("Dropbox/CovidBeliefsBehaviorsNormsSurvey/covid_survey_responses.txt.gz",sep="\t",compression="gzip");
num_rows = data.shape[0]

col_names = ["id","country","age","gender","education","us_state","india_state",
             "vaccine_accept","risk_community","community_action_importance","community_action_norms","distancing_familiarity",
             "prevention_distancing","prevention_mask","future_vaccine","flu_vaccine","density","work_industry",
             "effect_mask","norms_vaccine",'weight_demo','weight_full_survey','weight_internet_demo','weight_internet_full_survey','wave']

data = data[col_names];
data = data.rename(columns={"id": "record_id"});

data = data.dropna(subset=["record_id","country","age","gender"]); # these are required
data["country"] = data["country"].apply(convertCountryToISO2)
data["us_state"] = data["us_state"].apply(convertUSState)
data["india_state"] = data["india_state"].apply(convertIndiaState)
data["wave"] = data["wave"].apply(convertWaveToString)
data["education"] = data["education"].apply(processEducation)
data["placebo"] = data["weight_demo"].apply(lambda x: 1)
data["weight_demo_square"] = data["weight_demo"].apply(lambda x: x**2)

data["gender"] = data["gender"].str.lower()
data["age"] = data["age"].str.lower()

data.to_csv("../data/processed_data.txt.gz",sep="\t",compression='gzip')
