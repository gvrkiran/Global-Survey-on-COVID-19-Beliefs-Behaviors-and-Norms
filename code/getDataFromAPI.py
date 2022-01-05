# script to plot vaccine norms vs. vaccine acceptance for snapshot countries

import sys,json,os;

f = open("../data/waves_snapshot_countries.txt");
lines = f.readlines();
dict_countries_mapping = {};
dict_wave_countries_mapping = {};

for line in lines:
    line = line.strip();
    line_split = line.split(",");
#    if(line_split[2]=="snapshot"):
    dict_countries_mapping[line_split[0]] = 1;
    if(line_split[2]=="waves"):
        dict_wave_countries_mapping[line_split[0]] = 1;

## uses data from questions "vaccine_accept: If a vaccine for COVID-19 becomes available, would you choose to get vaccinated?"
## and "norms_vaccine: Out of 100 people in your community, how many do you think would take the COVID-19 vaccine if it were made available?"

out = open("../data/vaccine_accept_vaccine_norms_waves_and_snapshot.txt","w");
out.write("country,vaccine_accept,norms_vaccine\n");

for country in dict_countries_mapping.keys():
    print(country,file=sys.stderr);
    command1 = "wget -O 1.json 'http://covidsurvey.mit.edu:5000/query?age=all&gender=all&country=" + country + "&signal=vaccine_accept'"
    os.system(command1);
    command2 = "wget -O 2.json 'http://covidsurvey.mit.edu:5000/query?age=all&gender=all&country=" + country + "&signal=norms_vaccine'"
    os.system(command2);

    f1 = open("1.json");
    line1 = f1.read();
    json_data1 = json.loads(line1);
    f2 = open("2.json");
    line2 = f2.read();
    json_data2 = json.loads(line2);
    val2 = (json_data2["norms_vaccine"]["weighted"])/100;
    val1 = json_data1["vaccine_accept"]["weighted"]["Yes"] + json_data1["vaccine_accept"]["weighted"]["Don't know"] + (json_data1["vaccine_accept"]["weighted"]["I have already been vaccinated"] if "I have already been vaccinated" in json_data1["vaccine_accept"]["weighted"] else 0);
    out.write(country + "," + str(val1) + "," + str(val2) + "\n");

out.close();

## uses data from two questions: "Information Medium: In the past week, from which of the following, if any, have you received news and information about COVID-19? Select all that apply."
## and "Information Sources: In the past week, from which of the following, if any, have you received news and information about COVID-19? Select all that apply."
out1 = open("../data/news_sources_mediums_consume_trust.txt","w");
out1.write("country,consume,trust,val\n");

for country in dict_wave_countries_mapping.keys():
    command1 = 'wget -O "1.json" "http://covidsurvey.mit.edu:5000/query?age=all&gender=all&country=' + country + '&signal=news_sources&wave=all"';
    os.system(command1);
    command2 = 'wget -O "2.json" "http://covidsurvey.mit.edu:5000/query?age=all&gender=all&country=' + country + '&signal=news_sources_trust&wave=all"';
    os.system(command2);

    f1 = open("1.json")
    line1 = f1.read();
    json_data1 = json.loads(line1);
    f2 = open("2.json")
    line2 = f2.read();
    json_data2 = json.loads(line2);
    val1_govt = json_data1["news_sources"]["government_health_authorities"]["weighted"]["Yes"];
    val2_govt = json_data2["news_sources_trust"]["government_health_authorities"]["weighted"]["Trust"];# + json_data2["news_sources_trust"]["government_health_authorities"]["weighted"]["Somewhat trust"];
    val1_journalists = json_data1["news_sources"]["journalists"]["weighted"]["Yes"];
    val2_journalists = json_data2["news_sources_trust"]["journalists"]["weighted"]["Trust"];# + json_data2["news_sources_trust"]["journalists"]["weighted"]["Somewhat trust"];
    val1_local_health = json_data1["news_sources"]["local_health_workers"]["weighted"]["Yes"];
    val2_local_health = json_data2["news_sources_trust"]["local_health_workers"]["weighted"]["Trust"];# + json_data2["news_sources_trust"]["local_health_workers"]["weighted"]["Somewhat trust"];
    val1_people_dontknow = json_data1["news_sources"]["ordinary_people_i_dont_know_personally"]["weighted"]["Yes"];
    val2_people_dontknow = json_data2["news_sources_trust"]["ordinary_people_i_do_not_know_personally"]["weighted"]["Trust"];# + json_data2["news_sources_trust"]["ordinary_people_i_do_not_know_personally"]["weighted"]["Somewhat trust"];
    val1_people_know = json_data1["news_sources"]["ordinary_people_i_know_personally"]["weighted"]["Yes"];
    val2_people_know = json_data2["news_sources_trust"]["ordinary_people_i_know_personally"]["weighted"]["Trust"];# + json_data2["news_sources_trust"]["ordinary_people_i_know_personally"]["weighted"]["Somewhat trust"];
    val1_politicians = json_data1["news_sources"]["politicians"]["weighted"]["Yes"];
    val2_politicians = json_data2["news_sources_trust"]["politicians"]["weighted"]["Trust"];# + json_data2["news_sources_trust"]["politicians"]["weighted"]["Somewhat trust"];
    val1_scientists = json_data1["news_sources"]["scientists"]["weighted"]["Yes"];
    val2_scientists = json_data2["news_sources_trust"]["scientists"]["weighted"]["Trust"];# + json_data2["news_sources_trust"]["scientists"]["weighted"]["Somewhat trust"];
    val1_who = json_data1["news_sources"]["world_health_organization"]["weighted"]["Yes"];
    val2_who = json_data2["news_sources_trust"]["world_health_organization"]["weighted"]["Trust"];# + json_data2["news_sources_trust"]["world_health_organization"]["weighted"]["Somewhat trust"];
    
    tmp_str1 = country + "," + str(val1_govt) + "," + str(val2_govt) + ",government_health_authorities";
    out1.write(tmp_str1 + "\n");
    tmp_str1 = country + "," + str(val1_journalists) + "," + str(val2_journalists) + ",journalists";
    out1.write(tmp_str1 + "\n");
    tmp_str1 = country + "," + str(val1_local_health) + "," + str(val2_local_health) + ",local_health_workers";
    out1.write(tmp_str1 + "\n");
    tmp_str1 = country + "," + str(val1_people_dontknow) + "," + str(val2_people_dontknow) + ",ordinary_people_i_do_not_know_personally";
    out1.write(tmp_str1 + "\n");
    tmp_str1 = country + "," + str(val1_people_know) + "," + str(val2_people_know) + ",ordinary_people_i_know_personally";
    out1.write(tmp_str1 + "\n");
    tmp_str1 = country + "," + str(val1_politicians) + "," + str(val2_politicians) + ",politicians";
    out1.write(tmp_str1 + "\n");
    tmp_str1 = country + "," + str(val1_scientists) + "," + str(val2_scientists) + ",scientists";
    out1.write(tmp_str1 + "\n");
    tmp_str1 = country + "," + str(val1_who) + "," + str(val2_who) + ",world_health_organization";
    out1.write(tmp_str1 + "\n");

    command3 = 'wget -O "1.json" "http://covidsurvey.mit.edu:5000/query?age=all&gender=all&country=' + country + '&signal=news_mediums&wave=all"';
    os.system(command3);
    command4 = 'wget -O "2.json" "http://covidsurvey.mit.edu:5000/query?age=all&gender=all&country=' + country + '&signal=news_mediums_trust&wave=all"';
    os.system(command4);

    f1 = open("1.json")
    line1 = f1.read();
    json_data1 = json.loads(line1);
    f2 = open("2.json")
    line2 = f2.read();
    json_data2 = json.loads(line2);

    val1_messaging_apps = json_data1["news_mediums"]["messaging_apps"]["weighted"]["Yes"];
    val2_messaging_apps = json_data2["news_mediums_trust"]["messaging_apps"]["weighted"]["Trust"];# + json_data2["news_mediums_trust"]["messaging_apps"]["weighted"]["Somewhat trust"];
    val1_newspapers = json_data1["news_mediums"]["newspapers"]["weighted"]["Yes"];
    val2_newspapers = json_data2["news_mediums_trust"]["newspapers"]["weighted"]["Trust"];# + json_data2["news_mediums_trust"]["newspapers"]["weighted"]["Somewhat trust"];
    val1_online_sources = json_data1["news_mediums"]["online_sources"]["weighted"]["Yes"];
    val2_online_sources = json_data2["news_mediums_trust"]["online_sources"]["weighted"]["Trust"];# + json_data2["news_mediums_trust"]["online_sources"]["weighted"]["Somewhat trust"];
    val1_radio = json_data1["news_mediums"]["radio"]["weighted"]["Yes"];
    val2_radio = json_data2["news_mediums_trust"]["radio"]["weighted"]["Trust"];# + json_data2["news_mediums_trust"]["radio"]["weighted"]["Somewhat trust"];
    val1_television = json_data1["news_mediums"]["television"]["weighted"]["Yes"];
    val2_television = json_data2["news_mediums_trust"]["television"]["weighted"]["Trust"];# + json_data2["news_mediums_trust"]["television"]["weighted"]["Somewhat trust"];

    tmp_str2 = country + "," + str(val1_messaging_apps) + "," + str(val2_messaging_apps) + ",messaging_apps";
    out1.write(tmp_str2 + "\n");
    tmp_str2 = country + "," + str(val1_newspapers) + "," + str(val2_newspapers) + ",newspapers";
    out1.write(tmp_str2 + "\n");
    tmp_str2 = country + "," + str(val1_online_sources) + "," + str(val2_online_sources) + ",online_sources";
    out1.write(tmp_str2 + "\n");
    tmp_str2 = country + "," + str(val1_radio) + "," + str(val2_radio) + ",radio";
    out1.write(tmp_str2 + "\n");
    tmp_str2 = country + "," + str(val1_television) + "," + str(val2_television) + ",television";
    out1.write(tmp_str2 + "\n");

#    break;

out1.close();

out_effective_sample_size = open("../data/effective_sample_size_timeseries.txt","w");
out_sample_size = open("../data/sample_size_timeseries.txt","w");

tmp_str = "country,";
for i in range(1,20):
    wave_param = "wave" + str(i);
    tmp_str += wave_param + ",";

out_effective_sample_size.write(tmp_str.strip(",") + "\n");
out_sample_size.write(tmp_str.strip(",") + "\n");

for country in dict_wave_countries_mapping.keys():
    command = 'wget -O "1.json" "http://covidsurvey.mit.edu:5000/query?age=all&gender=all&country=' + country + '&signal=mismatch_index&timeseries=true"';
    os.system(command);
    print(country);

    f = open("1.json")
    line = f.read();
    json_data = json.loads(line);
    
    tmp_str = country + ",";
    tmp_str_effective_sample_size = country + ",";
    tmp_str_sample_size = country + ",";
    for i in range(1,20):
        wave_param = "wave" + str(i);
        tmp_str_effective_sample_size += str(json_data[wave_param]["effective_sample_size"]) + ",";
        tmp_str_sample_size += str(json_data[wave_param]["results_count"]) + ",";

    out_effective_sample_size.write(tmp_str_effective_sample_size.strip(",") + "\n");
    out_sample_size.write(tmp_str_sample_size.strip(",") + "\n");

out_effective_sample_size.close();
out_sample_size.close();
