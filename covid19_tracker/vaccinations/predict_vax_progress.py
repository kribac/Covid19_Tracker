import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import Span

FILE_VAX_TIMESERIES = '../../data/germany_vaccinations_timeseries_v2.tsv'
FILE_DELIVERIES_TIMESERIES = '../../data/germany_deliveries_timeseries_v2.tsv'
FILE_VAX_BY_STATE = '../../data/germany_vaccinations_by_state.tsv'

# Q2 deliveries
# FILE_DELIVERY_PROGNOSIS = "../../data/impfung_lieferprognoseQ2_stand210507.csv"

# Q2 deliveries + estimates for Q3
FILE_DELIVERY_PROGNOSIS = "../../data/impfung_lieferprognoseQ2Q3_stand210517.csv"


# determine which vaccines are considered in vaccination campaign
USE_VACCINES = {
    "BIONTECH": True,
    "MODERNA": True,
    "ASTRAZENECA":True,
    "JJ": False
}

DELIVERY_PREDICTION = "prognosis" #"static", "prognosis"
# DELIVERY_PREDICTION = "static" #"static", "prognosis"


SHOW_BIONTECH = True
SHOW_AZ = True
SHOW_MODERNA = True
SHOW_JJ = False

END_DATE = "2021-09-30"


PERSONS_TO_VACCINATE = 51087903 # from "pandemieende.de"
POPULATION_GERMANY = 83190556


def load_vax_timeseries(file_vax_ts):
    vax_ts = pd.read_csv(FILE_VAX_TIMESERIES, sep='\t', index_col="date")
    vax_ts.index = pd.to_datetime(vax_ts.index, format="%Y-%m-%d")
    return vax_ts

def load_planned_deliveries(file_planned_deliveries):
    planned_doses = pd.read_csv(FILE_DELIVERY_PROGNOSIS, sep=";", index_col="Wochenmontag",
                                usecols=["Wochenmontag", "Biontech", "Moderna"])
    planned_doses.index = pd.to_datetime(planned_doses.index, format="%d.%m.%Y")
    return planned_doses


class VaxPredictor:

    def __init__(self, use_vaccines=USE_VACCINES, end_date=END_DATE):
        self.USE_BIONTECH = use_vaccines["BIONTECH"]
        self.USE_MODERNA = use_vaccines["MODERNA"]
        self.USE_ASTRAZENECA = use_vaccines["ASTRAZENECA"]
        self.USE_JJ = use_vaccines["JJ"]

        self.END_DATE = pd.to_datetime(end_date, format="%Y-%m-%d")

    def loadData(self, file_vax_ts=FILE_VAX_TIMESERIES):
        self.vax_ts = load_vax_timeseries(file_vax_ts)
        self.START_DATE = self.vax_ts.index[0]
        self.TODAY = self.vax_ts.index[-1]


    def _loadDeliveryPrognosis(self, reindex2Daily=True):
        """
        if reindexToDaily is True: transform weekly deliveries to daily, assuming that deliveries are distributed evenly over week
        """
        df = load_planned_deliveries(FILE_DELIVERY_PROGNOSIS)

        # = pd.date_range(START_DATE, END_DATE)

        if reindex2Daily:
            idx_new = pd.date_range(self.START_DATE, self.END_DATE)
            df = df.reindex(idx_new, method="ffill", fill_value=0)
            df.Biontech = df.Biontech / 7  # from weekly doses to daily
            df.Moderna = df.Moderna / 7

        self.deliveries_planned = df

    def _expandDataframe(self):
        """
        add new columns to dataframe for predicitons
        """
        self.vax_ts["est_bedarf_biontech_zweit_kumulativ"] = 0 # total doses needed for 2nd shot
        self.vax_ts["est_bedarf_biontech_zweit_rest"] = 0 # remaining doses needed for 2nd shot
        # self.vax_ts["est_dosen_biontech_kumulativ"] = 0
        # self.vax_ts["est_dosen_biontech_erst_kumulativ"] = 0
        # self.vax_ts["est_dosen_biontech_zweit_kumulativ"] = 0

        self.vax_ts["est_bedarf_moderna_zweit_kumulativ"] = 0  # total doses needed for 2nd shot
        self.vax_ts["est_bedarf_moderna_zweit_rest"] = 0  # remaining doses needed for 2nd shot

        self.vax_ts["est_bedarf_astrazeneca_zweit_kumulativ"] = 0  # total doses needed for 2nd shot
        self.vax_ts["est_bedarf_astrazeneca_zweit_rest"] = 0  # remaining doses needed for 2nd shot

    def _compute2ndDoseNeeds(self, day):
        """
        compute number of doses needed for 2nd shots for a single day
        Assumptions:
        - Biontech: 6 weeks between shots
        """

        day_minus6w = day - pd.to_timedelta(6, 'W')
        day_minus12w = day - pd.to_timedelta(12, 'W')
        day_before = day - pd.to_timedelta(1, 'D') # one day earlier

        # Biontech
        if self.USE_BIONTECH:

            if day_minus6w > self.START_DATE:
                doses_first_prev = self.vax_ts.loc[day_minus6w].dosen_biontech_erst_kumulativ # first shots 6 weeks ago
                doses_second_rest = doses_first_prev - self.vax_ts.loc[day_before].dosen_biontech_zweit_kumulativ
                self.vax_ts.at[day, "est_bedarf_biontech_zweit_kumulativ"] = doses_first_prev
                self.vax_ts.at[day, "est_bedarf_biontech_zweit_rest"] = doses_second_rest
                # print(f"{day}: {self.vax_ts.loc[day].est_bedarf_biontech_zweit_rest}")

        if self.USE_MODERNA:

            if day_minus6w > self.START_DATE:
                doses_first_prev = self.vax_ts.loc[day_minus6w].dosen_moderna_erst_kumulativ  # first shots 6 weeks ago
                doses_second_rest = doses_first_prev - self.vax_ts.loc[day_before].dosen_moderna_zweit_kumulativ
                self.vax_ts.at[day, "est_bedarf_moderna_zweit_kumulativ"] = doses_first_prev
                self.vax_ts.at[day, "est_bedarf_moderna_zweit_rest"] = doses_second_rest

        if self.USE_ASTRAZENECA:

            if day_minus12w > self.START_DATE:
                doses_first_prev = self.vax_ts.loc[day_minus12w].dosen_astrazeneca_erst_kumulativ  # first shots 12 weeks ago
                doses_second_rest = doses_first_prev - self.vax_ts.loc[day_before].dosen_astrazeneca_zweit_kumulativ
                self.vax_ts.at[day, "est_bedarf_astrazeneca_zweit_kumulativ"] = doses_first_prev
                self.vax_ts.at[day, "est_bedarf_astrazeneca_zweit_rest"] = doses_second_rest



    def _predictVaccinations(self, day):
        """
        step 1: static capabilities, fully satisfy 2nd dose needs
        """

        day_before = day - pd.to_timedelta(1, 'D')

        # values estimated based on week 28.4.-5.5.
        if DELIVERY_PREDICTION == "static":
            capacity_biontech = 547441 # daily
            capacity_moderna = 50901
        elif DELIVERY_PREDICTION == "prognosis":
            capacity_biontech = self.deliveries_planned.loc[day].Biontech
            capacity_moderna = self.deliveries_planned.loc[day].Moderna

        capacity_astrazeneca = 64796 # no clear delivery prognoses for az available yet
        #capacity_astrazeneca = 100000  # no clear delivery prognoses for az available yet

        total_first_shots = 0 # keep track of all daily shots of all vaccines
        total_second_shots = 0

        if self.USE_BIONTECH:
            need_2nd_dose = self.vax_ts.loc[day].est_bedarf_biontech_zweit_rest
            second_shots = need_2nd_dose
            first_shots = max(0, capacity_biontech-second_shots)

            total_first_shots += first_shots
            total_second_shots += second_shots

            self.vax_ts.at[day, "dosen_biontech_erst_kumulativ"] = self.vax_ts.loc[day_before].dosen_biontech_erst_kumulativ + first_shots
            self.vax_ts.at[day, "dosen_biontech_zweit_kumulativ"] = self.vax_ts.loc[day_before].dosen_biontech_zweit_kumulativ + second_shots
            self.vax_ts.at[day, "dosen_biontech_kumulativ"] = self.vax_ts.loc[day_before].dosen_biontech_kumulativ + first_shots + second_shots

        if self.USE_MODERNA:
            need_2nd_dose = self.vax_ts.loc[day].est_bedarf_moderna_zweit_rest
            second_shots = need_2nd_dose
            first_shots = max(0, capacity_moderna - second_shots)

            total_first_shots += first_shots
            total_second_shots += second_shots

            self.vax_ts.at[day, "dosen_moderna_erst_kumulativ"] = self.vax_ts.loc[
                                                                       day_before].dosen_moderna_erst_kumulativ + first_shots
            self.vax_ts.at[day, "dosen_moderna_zweit_kumulativ"] = self.vax_ts.loc[
                                                                        day_before].dosen_moderna_zweit_kumulativ + second_shots
            self.vax_ts.at[day, "dosen_moderna_kumulativ"] = self.vax_ts.loc[
                                                                  day_before].dosen_moderna_kumulativ + first_shots + second_shots

        if self.USE_ASTRAZENECA:
            need_2nd_dose = self.vax_ts.loc[day].est_bedarf_astrazeneca_zweit_rest
            second_shots = need_2nd_dose
            first_shots = max(0, capacity_astrazeneca-second_shots)

            total_first_shots += first_shots
            total_second_shots += second_shots

            self.vax_ts.at[day, "dosen_astrazeneca_erst_kumulativ"] = self.vax_ts.loc[day_before].dosen_astrazeneca_erst_kumulativ + first_shots
            self.vax_ts.at[day, "dosen_astrazeneca_zweit_kumulativ"] = self.vax_ts.loc[day_before].dosen_astrazeneca_zweit_kumulativ + second_shots
            self.vax_ts.at[day, "dosen_astrazeneca_kumulativ"] = self.vax_ts.loc[day_before].dosen_astrazeneca_kumulativ + first_shots + second_shots

        # update total dose count
        self.vax_ts.at[day, "dosen_kumulativ"] = self.vax_ts.loc[day_before].dosen_kumulativ + total_first_shots + total_second_shots
        self.vax_ts.at[day, "personen_erst_kumulativ"] = self.vax_ts.loc[day_before].personen_erst_kumulativ + total_first_shots
        self.vax_ts.at[day, "personen_voll_kumulativ"] = self.vax_ts.loc[day_before].personen_voll_kumulativ + total_first_shots



    def predictVaxTS(self):

        # first, expand date range
        idx_new = pd.date_range(self.START_DATE, self.END_DATE)
        self.vax_ts = self.vax_ts.reindex(idx_new, fill_value=0)

        self._loadDeliveryPrognosis()

        # add additional columns to hold vaccination predictions
        self._expandDataframe()

        for i in range(len(self.vax_ts)):

            day = self.vax_ts.index[i]

            #1 - compute needs for second dose
            self._compute2ndDoseNeeds(day)

            #2 - predict future vaccinations
            if day > self.TODAY: # we only predict the future
                self._predictVaccinations(day)






if __name__ == "__main__":

    vax_predictor = VaxPredictor(use_vaccines=USE_VACCINES, end_date=END_DATE)

    vax_predictor.loadData(FILE_VAX_TIMESERIES)
    vax_predictor.predictVaxTS()

    vax_ts = vax_predictor.vax_ts

    vax_ts_rolling = vax_ts.rolling(7).mean()


    vax_ts["personen_ziel"] = PERSONS_TO_VACCINATE
    vax_ts["dreiviertel_deutsche"] = 0.75*POPULATION_GERMANY



    status_fist_shots = vax_ts.personen_erst_kumulativ.loc[vax_predictor.TODAY]
    print(f"people with one shot: {status_fist_shots}")
    print(f"this is {status_fist_shots/POPULATION_GERMANY*100}% of the total population")
    print(f"this is {status_fist_shots / (0.75*POPULATION_GERMANY) * 100}% of 75% of all Germans")

    p1 = figure(x_axis_type="datetime", plot_height=600, plot_width=1000)

    p1.line(vax_ts.index, vax_ts.personen_ziel, line_width=2, line_color="red", line_dash="dashed", legend_label="Impfziel Erwachsene")
    p1.line(vax_ts.index, vax_ts.dreiviertel_deutsche, line_width=2, line_color="red", line_dash="dashed",
            legend_label="75% der Bevölkerung")

    p1.line(vax_ts.index, vax_ts.dosen_kumulativ, line_width=2, line_color='black', legend_label="dosen gesamt")
    p1.line(vax_ts.index, vax_ts.personen_erst_kumulativ, line_width=1, line_color="black", legend_label="dosen erst")
    p1.line(vax_ts.index, vax_ts.personen_voll_kumulativ, line_width=1, line_color="black", line_dash="dashed",
            legend_label="dosen zweit")

    if SHOW_BIONTECH:
        p1.line(vax_ts.index, vax_ts.dosen_biontech_kumulativ, line_color="red", line_width=2,
                legend_label="BioNTech gesamt")
        p1.line(vax_ts.index, vax_ts.dosen_biontech_erst_kumulativ, line_color="red", line_width=1,
                legend_label="BioNTech erst")
        p1.line(vax_ts.index, vax_ts.dosen_biontech_zweit_kumulativ, line_color="red", line_dash="dashed",
                legend_label="BioNTech zweit")
        # p1.line(vax_ts.index, vax_ts.est_bedarf_biontech_zweit_kumulativ, line_color="orange", line_dash="solid",
        #         legend_label="Bedarf zweit kumulativ (geschätzt)")
        p1.line(vax_ts.index, vax_ts.est_bedarf_biontech_zweit_rest, line_color="orange", line_dash="dashed",
                legend_label="Bedarf Biontech zweit Rest (geschätzt)")

    # p1.line(vax_ts.index, vax_ts.est_dosen_biontech_erst_kumulativ, line_color="orange", line_width=1,
    #         legend_label="Prädikiton BioNTech erst")
    # p1.line(vax_ts.index, vax_ts.est_dosen_biontech_zweit_kumulativ, line_color="orange", line_dash="dashed",
    #         legend_label="Prädiktion BioNTech zweit")

    if SHOW_AZ:
        p1.line(vax_ts.index, vax_ts.dosen_astrazeneca_kumulativ, line_color="green", line_width=2,
                legend_label="AstraZeneca gesamt")
        p1.line(vax_ts.index, vax_ts.dosen_astrazeneca_erst_kumulativ, line_color="green", line_width=1,
                legend_label="AstraZeneca erst")
        p1.line(vax_ts.index, vax_ts.dosen_astrazeneca_zweit_kumulativ, line_color="green", line_width=1,
                line_dash="dashed", legend_label="AstraZeneca zweit")
        p1.line(vax_ts.index, vax_ts.est_bedarf_astrazeneca_zweit_kumulativ, line_color="lightgreen", line_width=1,
                line_dash="dashed", legend_label="Bedarf AstraZeneca zweit rest (geschätzt)")

    if SHOW_MODERNA:
        p1.line(vax_ts.index, vax_ts.dosen_moderna_kumulativ, line_color="blue", line_width=2,
                legend_label="Moderna gesamt")
        p1.line(vax_ts.index, vax_ts.dosen_moderna_erst_kumulativ, line_color="blue", line_width=1,
                legend_label="Moderna erst")
        p1.line(vax_ts.index, vax_ts.dosen_moderna_zweit_kumulativ, line_color="blue", line_width=1, line_dash="dashed",
                legend_label="Moderna zweit")
        p1.line(vax_ts.index, vax_ts.est_bedarf_moderna_zweit_rest, line_color="aqua", line_width=1,
                line_dash="dashed", legend_label="Bedarf Moderna zweit rest (geschätzt)")

    # p1.line(vax_predictor.deliveries_planned.index, vax_predictor.deliveries_planned.Biontech, line_color="brown", line_width=1,
    #         legend_label="Biontech plan")
    vline = Span(location=vax_predictor.TODAY, dimension='height', line_color='black', line_width=1, line_dash="dashed")
    p1.renderers.extend([vline])
    p1.legend.location = "top_left"

    show(p1)