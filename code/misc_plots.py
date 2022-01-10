import logging

import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats
import CovidSurvey
import datetime as dt
import logging
import os
import json
import numpy as np
import patsy
import statsmodels.formula.api as smf
import seaborn as sns
import matplotlib
from ResearchTools import ChartTools
import matplotlib.pyplot as plt
import tqdm

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams['font.size'] = 13
matplotlib.rcParams['patch.antialiased'] = True
matplotlib.rcParams['patch.linewidth'] = 0.5

log = logging.Logger(name='nhb')

# TODO: Remove hard-coded paths and "moehring" from all strings
if CovidSurvey.Helper.is_linux():
    out_path = '/home/moehring/bin/CovidSurvey/analysis/tech_report'
else:
    out_path = 'C:\\Users\\moehring\\git\\CovidSurvey\\analysis\\tech_report'
fig_path = os.path.join(out_path, 'figs')

if not os.path.exists(fig_path):
    os.makedirs(fig_path)

block2col = {
    'demographics': ['age', 'gender', 'country', 'education', 'own_health', 'density'],
    'vaccineandhealthcare': ['vaccine_accept', 'knowledge_existing_treatments'],
    'covid-19informationexposure': ['info_exposure_past_week', 'info_exposure_more_less_wanted'],
    'knowledgeandpositivecases': ['know_positive_case', 'knowledge_existing_treatments'],
    'information': ['news_medium_*', 'news_sources_*'],
    'preventionbehaviorsinpractice': ['prevention_mask', 'prevention_distancing', 'prevention_hand_washing'],
    'ben': ['effect_mask', 'measures_taken_*', 'effect_hand_washing', 'country_management', 'community_management', 'community_action_importance',
            'community_action_norms'],
    'distancingfamiliarity,importance&norms': ['distancing_importance', 'distancing_norms_maintain_a_distance_of_at_least_1_meter_from_others',
                                               'distancing_norms_wear_a_face_mask_or_covering', 'norms_vaccine'],
    'futureactions': ['future_vaccine', 'future_masks', 'future_dist'],
    'riskperceptionsandlocusofcontrol': ['risk_community', 'risk_infection', 'control_infection', 'infection_severity'],
    'work': ['employed_2020', 'work_changes', 'work_type', 'work_industry'],
    'intentionstovisit': ['locations_would_attend_*'],
    'surveyresponseinformation': []
}
col2block = {}
for tmp_b in block2col:
    for tmp_c in block2col[tmp_b]:
        col2block[tmp_c] = tmp_b
cleancol2block = {'country_cov': 'demographics'}

reverse_label_map = {
    "vaccine_accept": {
        "Yes": 2,
        "Don't know": 1,
        "No": 0
    },
    "future_masks": {
        "Always": 4,
        "Almost always": 3,
        "When convenient": 2,
        "Rarely": 1,
        "Never": 0
    },
    "future_dist": {
        "Always": 4,
        "Almost always": 3,
        "When convenient": 2,
        "Rarely": 1,
        "Never": 0
    },
    "future_vaccine": {
        "Yes, definitely": 4,
        "Probably": 3,
        "Unsure": 2,
        "Probably not": 1,
        "No, definitely not": 0
    }
}
label_map = {}
for q_name in reverse_label_map:
    label_map[q_name] = {}
    for answer_text in reverse_label_map[q_name]:
        num_answer = reverse_label_map[q_name][answer_text]
        assert num_answer not in label_map[q_name]
        label_map[q_name][num_answer] = answer_text


###################
# preprocess data #
###################


def weighted_mean(series, weights):
    # remove elements w/ null values or weights
    ixs = ~(pd.isna(series) | pd.isna(weights) | (weights <= 0))
    to_ret = np.average(series[ixs], weights=weights[ixs])
    if pd.isna(to_ret):
        log.info(ixs.sum())
        log.info(len(series))
        log.info(series[ixs])
        log.info(weights[ixs])
    assert not pd.isna(to_ret)
    return to_ret


def normalize_weights(df):
    # for each wave, normalize weights so they sum to the number of responses in each country
    weight_cols = [el for el in df.columns if 'weight' in el]
    for wave in df.wave.unique():
        for country in df.country.unique():
            if pd.isna(country) or pd.isna(wave):
                continue
            for c in weight_cols:
                ixs = pd.Series((df.country == country) & (df.wave == wave) & ~pd.isna(df[c]))
                num_responses = ixs.sum()
                df.loc[ixs, c] = df.loc[ixs, c] / df.loc[ixs, c].sum() * num_responses
    return df


def weight_plots(df):
    countries = [el for el in df.country.unique() if not pd.isna(el)]
    aggs = {'Weighted': pd.DataFrame(index=countries), 'Unweighted': pd.DataFrame(index=countries)}

    # filter to only include males or females
    df = df.loc[df.weight_full_survey > 0].copy()
    df['female'] = (df.gender == 2).apply(int)

    for c in countries:
        tmp = df.loc[df.country == c]

        # weighted estimates
        mod = smf.wls('female ~ 1', data=tmp, weights=tmp.weight_full_survey).fit()
        aggs['Weighted'].loc[c, 'Estimate'] = mod.params.iloc[0]
        aggs['Weighted'].loc[c, 'SE'] = mod.bse.iloc[0]

        # unweighted estimates
        mod = smf.wls('female ~ 1', data=tmp, weights=tmp.unweighted).fit()
        aggs['Unweighted'].loc[c, 'Estimate'] = mod.params.iloc[0]
        aggs['Unweighted'].loc[c, 'SE'] = mod.bse.iloc[0]
    for k in aggs:
        aggs[k]['group'] = k
    country_order = list(aggs['Unweighted'].sort_values('Estimate').index)
    aggs = pd.concat([aggs['Weighted'], aggs['Unweighted']], axis=0)
    aggs = aggs.loc[country_order]
    ChartTools.plot_coefs(coefs=aggs, fn=os.path.join(fig_path, 'weight_fig_gender.pdf'), pickle_fig=False, line_loc=0.5, xlabel='Share female', markersize=3)


def weight_plots_wave(df):
    df = df.copy()
    df = df.loc[~pd.isna(df.wave)]
    df = df.loc[~pd.isna(df.country)].copy()

    vs = ['age']
    weight_col = 'weight_demo'
    fp = os.path.join(fig_path, 'weight_plots')
    if not os.path.exists(fp):
        os.makedirs(fp)
    waves = [el for el in df.wave.unique() if not pd.isna(el)]
    print(waves)
    aggs = dict((v, pd.DataFrame(index=waves)) for v in vs)
    for c in df.country.unique():
        tmp_c = df.loc[df.country == c]
        for v in vs:
            tmp = tmp_c.loc[~pd.isna(tmp_c[v]) & (tmp_c[v] >= 0)]
            for w in waves:
                tt = tmp.loc[tmp.wave == w]
                aggs[v].loc[w, c] = weighted_mean(tt[v], tt[weight_col])

    # now plot
    for v in aggs:
        fn = os.path.join(fp, v + '.pdf')
        fig, ax = plt.subplots()
        print(aggs[v])
        aggs[v].plot(ax=ax)
        ChartTools.save_show_plot(fig=fig, fn=fn, pickle_fig=False, show_graph=False)


def country_summary(df):
    fp = os.path.join(fig_path, 'summary')
    if not os.path.exists(fp):
        os.makedirs(fp)
    rows = {}
    for c in tqdm.tqdm(df.groupby('country')):
        if len(c[1]) < 100:
            continue
        rows[c[0]] = {
            'Survey type': c[1]['survey_type'].iloc[0],
            'Number of starts': len(c[1]),
            'Number of completes': int(c[1].finished.sum())
        }
    aggs = pd.DataFrame(rows).T
    aggs.to_csv(os.path.join(fp, 'country_counts.csv'))
    good_countries = set(aggs.index)
    print(aggs)

    aggs = df.loc[(df.finished == 1) & (df.country.isin(good_countries))].groupby(['country', 'language']).id.nunique().unstack().fillna(0)
    aggs = aggs.div(aggs.sum(axis=1), axis=0)
    plt.close('all')
    fig, ax = plt.subplots()
    sns.set(font_scale=0.1)
    sns.heatmap(
        data=aggs,
        ax=ax,
        xticklabels=True,
        yticklabels=True,
    )
    ChartTools.save_show_plot(fig=fig, fn=os.path.join(fp, 'languages.pdf'), pickle_fig=False, show_graph=False)

    # also make a table of top k languages and their percentages
    k = 3
    ls = pd.DataFrame('', index=good_countries, columns=[el for el in range(k)])
    for c in good_countries:
        row = aggs.loc[c].sort_values(ascending=False)
        for kk in range(k):
            ls.loc[c, kk] = '{0} ({1:.1f}%)'.format(row.index[kk], row.iloc[kk]*100)
    ls.columns = ['Top {0} language'.format(el + 1) for el in ls.columns]
    ls.to_csv(os.path.join(fp, 'languages.csv'))
    ls.to_latex(os.path.join(fp, 'languages.tex'))


def main():
    if CovidSurvey.Helper.is_linux():
        data_path = '/nfs/sloanlab004/projects/covid_survey_proj/data/cleaned_exports/processed_data'
    else:
        data_path = 'C:\\Users\\moehring\\Dropbox (MIT)\\CovidBeliefsBehaviorsNormsSurvey_Preview\\ProcessedData'
    fn = os.path.join(data_path, 'covid_survey_responses_numeric.txt.gz')
    full_df = pd.read_table(fn, sep='\t', low_memory=False)

    df = full_df.copy()
    # df.display_order = df.display_order.apply(json.loads)
    df = normalize_weights(df)
    df['unweighted'] = 1

    #############################
    # Data Cleaning & Filtering #
    #############################
    country_summary(df)
    weight_plots_wave(df)
    weight_plots(df)


# if __name__ == '__main__':
#     main()
