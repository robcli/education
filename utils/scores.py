import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class Scores:
    def __init__(self):
        self.df = None

    @classmethod
    def create_from_table(cls, df: pd.DataFrame):
        instance = cls.__new__(cls)
        instance.df = df
        return instance
    
    def merge(self, Scores_obj):
        merged_df = pd.concat([self.df, Scores_obj.df])
        new_instance = self.create_from_table(merged_df)
        return new_instance
    
    def plot(self, states=None, section: str=None, exclude: bool=False):
        fig, ax = plt.subplots()

        if not section:
            print("Warning, no section was given and the plot will be empty!")
        scores = (self.get_states(states, exclude=exclude)
                  .get_section(section)
                  .df)
        
        sns.lineplot(data = scores,
             x = "year",
             y = "mean",
             hue = "location",
             marker = "o")

        ax.legend(loc = "center left", bbox_to_anchor = (1, 0.5))
        return fig
    
    def get_states(self, states, exclude: bool=False):
        scores = self.df.copy()
        if not states:
            return scores
        if exclude:
            scores = scores.query("location not in @states")
        else:
            scores = scores.query("location in @states")
        new_instance = self.create_from_table(scores)
        return new_instance

    def get_section(self, section):
        scores = self.df.copy()
        if section not in scores["section"].unique():
            raise KeyError(f"{section} is not a section in the data.")
        scores = scores[scores["section"] == section]
        new_instance = self.create_from_table(scores)
        return new_instance
    
    def get_year(self, year: int):
        scores = self.df.copy()
        scores = scores.query("year==@year")
        new_instance = self.create_from_table(scores)
        return new_instance
    
    def query(self, s: str):
        scores = self.df.copy()
        scores = scores.query(s)
        new_instance = self.create_from_table(scores)
        return new_instance

class SATScores(Scores):
    def __init__(self, path: str, sheet_name=None):
        super().__init__()
        self.df = self._clean(path, sheet_name=sheet_name)

    @classmethod
    def create_from_table(cls, df: pd.DataFrame):
        return super().create_from_table(df)

    def _clean(self, path: str, sheet_name=None):
        locations = pd.read_excel(path, skiprows=5, nrows=52).iloc[:, 0]
        columns = pd.read_excel(path, skiprows=1, nrows=52).columns
        years = [c for c in columns if isinstance(c, int)]
        dfs = []
        for i, j, year in zip(range(1, 23, 7), range(8, 30, 7), years):
            df = (pd.read_excel(path, 
                                skiprows=5, 
                                nrows=52)
                    .iloc[:, i:j]
                    .set_axis(["total_mean", "total_sd", "erw_mean", 
                            "erw_sd","math_mean", "math_sd", "percent"], 
                            axis=1)
                    .assign(year=year,
                            location=locations))
            df = df.drop(["total_sd", "math_sd", "erw_sd"], axis=1)
            dfs.append(df)
        
        bulk = pd.concat(dfs)
        final = bulk.melt(id_vars=["location", "year", "percent"], 
                        var_name="section",
                        value_name="mean")
        final["section"] = final["section"].str.replace("_mean", "")
        final["location"] = final["location"].str.strip()
        return final.assign(test="SAT")        
    
    def plot(self, states=None, section: str="total", exclude: bool=False):
        return super().plot(states=states, section=section, exclude=exclude)
        
    
    def get_states(self, states, exclude: bool=False):
        return super().get_states(states, exclude=exclude)
        
    def get_section(self, section):
        try:
            return super().get_section(section)
        except KeyError:
            raise KeyError(f"{section} is not valid. Try: ['total', 'math', 'erw']")
    
    def get_year(self, year: int):
        return super().get_year(year)
    
    def query(self, s: str):
        return super().query(s)
        

class ACTScores(Scores):
    def __init__(self, path, sheet_name=None):
        super().__init__()
        self.df = self._clean(path, sheet_name=sheet_name)

    @classmethod
    def create_from_table(cls, df: pd.DataFrame):
        return super().create_from_table(df)

    def _clean(self, path, sheet_name=None):
        years = pd.read_excel(path, skiprows=3).columns[-2:]
        df = pd.read_excel(path,
                           skiprows=4,
                           nrows=61,
                           names=["location", "composite_1", "english_1", "math_1", "reading_1", "science_1",
                                  "composite_2", "english_2", "math_2", "reading_2", "science_2",
                                  "percent_1", "percent_2"]).dropna()
        
        df["location"] = (df["location"].str.replace("\\.*", "", regex=True)
                          .str.strip())
                
        first_year = df[["location", "composite_1", "english_1", "math_1", "reading_1", "science_1", "percent_1"]]
        first_year = (first_year.assign(year = years[0])
                      .rename({c:c.replace("_1", "") for c in first_year.columns}, axis = 1))
        second_year = df[["location", "composite_2", "english_2", "math_2", "reading_2", "science_2", "percent_2"]]
        second_year = (second_year.assign(year = years[1])
                       .rename({c:c.replace("_2", "") for c in second_year.columns}, axis = 1))

        final = (pd.concat([first_year, second_year])
                 .melt(id_vars=["location", "year", "percent"], 
                       var_name="section",
                       value_name="mean"))
        return final.assign(test="ACT")
    
    def plot(self, states=None, section: str="composite", exclude: bool=False):
        return super().plot(states=states, section=section, exclude=exclude)


    def get_states(self, states, exclude: bool=False):
        return super().get_states(states, exclude=exclude)
        
    def get_section(self, section):
        try:
            return super().get_section(section)
        except KeyError:
            raise KeyError(f"{section} is not valid. Try: ['composite', 'math', 'english', 'reading', 'science']")
        
    def get_year(self, year: int):
        return super().get_year(year)
    
    def query(self, s: str):
        return super().query(s)
        
class NAEPScores(Scores):
    def __init__(self, path: str, sheet_name=None):
        super().__init__()
        self.df = self._clean(path, sheet_name=sheet_name)

    def _clean(self, path: str, sheet_name=None):
        header = pd.read_excel(path,
                               skiprows=1).columns[0]
        
        subject, grade, _ = [_.strip() for _ in header.split(",")]
        grade = grade.replace("Grade ", "")
        section = subject + "_" + grade

        df = pd.read_excel(path,
                           skiprows=8,
                           nrows=324).dropna()
        
        df = df.rename({"Jurisdiction":"location",
                        "Average scale score":"mean",
                        "Year":"year"}, axis=1)
        
        df = df.drop("All students", axis=1)
        df = df.assign(section = section)
        
        return df

    def get_states(self, states, exclude: bool=False):
        return super().get_states(states, exclude=exclude)
        
    def get_section(self, section):
        try:
            return super().get_section(section)
        except KeyError:
            raise KeyError(f"{section} is not valid.")
        
    def get_year(self, year: int):
        return super().get_year(year)
    
    def query(self, s: str):
        return super().query(s)

