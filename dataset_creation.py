#importing the fastf1 and pandas libraries
import fastf1
import pandas as pd

#enables the f1 cache (tells it to store the data locally instead of downloading it over and over)
fastf1.Cache.enable_cache('CHANGE_ME')

#these variables state the year and Grand Prix that will be loaded in the session
year  = 2023
gp = ["Bahrain", "Miami", "Monaco", "Spain"]

#this list states each part of the race weekend that has data that I want to use (FP1, FP2, FP3, Qualifying,
#and the actual race)
sessions = ["FP1", "FP2", "FP3", "Q", "R"]

#this creates two empty lists to put in the data for each session. this will be appended after each session
all_laps = []
all_results = []

#these lists keep the columns I want from each dataset
keep_cols_laps = ["LapTime", "Driver", "LapNumber", "IsPersonalBest", "Position", "Session", "Year", "GrandPrix"]
keep_cols_results = ["Abbreviation", "Position", "ClassifiedPosition", "Time", "Status", "Laps", "Session", "Year", "Grandprix"]

later_keep_cols = ["FP1 Lap Time", "FP1 Position", "FP2 Lap Time", "FP2 Position", "FP3 Lap Time", "FP3 Position", "Qualifying Lap Time", "Qualifying Position", "Race Position"]

for l in gp:
    #for each session in the list, it will pull out all of the data and puts it into temporary lists, then
    #takes out the columns i dont want, then narrows down their times to their best time, and then adds it to
    #the overall list.
    for s in sessions:

        drivers_list = []
        #gets and loads the session data for the specific session. Prints the session, year, and grandprix
        session = fastf1.get_session(year, l, s)
        session.load()
        print(f"Loaded {l} {year} {s}")

        #copies the data from the session data into a data frame for laps
        laps_df = session.laps.copy()
        laps_df["Session"] = s
        laps_df["Year"] = year
        laps_df["GrandPrix"] = l

        #copies the data from the session data into a data frame for results
        results_df = session.results.copy()
        results_df["Session"] = s
        results_df["Year"] = year
        results_df["Grandprix"] = l

        #keeps the columns in the data that I specified at the beginning
        laps_df = laps_df[[c for c in keep_cols_laps if c in laps_df.columns]]
        results_df = results_df[[c for c in keep_cols_results if c in results_df.columns]]

        #if the sessions are not the final results, it will keep their best lap time only
        if s != "R":
            #will only keep laps that were their best time
            laps_df = laps_df[laps_df["IsPersonalBest"] == True]

            #resets the row numbers (they get mixed up when you remove rows)
            laps_df = laps_df.reset_index(drop = True)   
            
            
        #this will loop through each driver and check if they have more than one best time. If they do, it
        #will remove their previous time (the worse one). It needs to go from 1 to 21 instead of 0 to twenty
        #because it gets an error when you get to the last person if you use 0 to 20.
        for i in range(1,21):
            #while the driver has multiple times, it will delete their extra times until there is 1 left
            while True:
                #uses try and accept for when it gets to the last driver and theres no line of that number
                try:
                    #if the driver of the two rows are the same, it will drop the line with the previous best 
                    #score. It then resets the index so that the lines are numbered correctly
                    if laps_df.iloc[i]["Driver"] == laps_df.iloc[(i-1)]["Driver"]:
                        laps_df = laps_df.drop(index = [i-1])
                        laps_df = laps_df.reset_index(drop = True) 
                    #if the two lines do not have the same driver, the while loop will break and it will go on
                    #to the next driver
                    else:
                        break
                #if the index is out of bounds, the while loop will break
                except IndexError:
                    break

        #if the session is one of the free practices, it will sort the lap times from shortest to longest
        if s == "FP1" or s == "FP2" or s == "FP3":
            laps_df = laps_df.sort_values(by='LapTime', ascending=True, inplace = False, na_position='last')
            laps_df = laps_df.reset_index(drop = True) 

        
        #if the session is not the race, it will give their final placing (that data was missing previously)
        if s != "R":
            for i in range(0,20):
                laps_df.loc[i, "Position"] = i+1
        
        results_df = results_df.reset_index(drop = True)
        #erases all data that is in final_results except the data that is from the race (we need this later to assign
        #placings)
        for i in range(len(results_df)):
            while True:
                #uses try and accept for when it gets to the last driver and theres no line of that number
                try:
                    if results_df.iloc[i]["Session"] != "R":
                        results_df = results_df.drop(index = [i])
                        results_df = results_df.reset_index(drop = True) 
                    else:
                        break
                #if the index is out of bounds, the while loop will break
                except IndexError:
                    break

        #this adds the current round's (FP1, FP2, etc.) laps and results to the full list
        all_laps.append(laps_df)
        all_results.append(results_df)

    #this sets what is on the axis for the laps and results data
    final_laps = pd.concat(all_laps)
    final_results = pd.concat(all_results)

    #this resets the all laps and all results data to use for the next race location
    all_laps = []
    all_results = []

    #resets the numbering of the rows
    final_laps = final_laps.reset_index(drop = True)
    final_results = final_results.reset_index(drop = True)


    #this goes down the list and finds where the same driver appears again. It then takes the data from the other
    #driver and saves it so that it can become a new column. 
    for i in range(0, 20): #there are 20 drivers per race
        for j in range(0,100): #there are 100 rows to compare it to

            #if the drivers are the same, it will save the data
            if final_laps.iloc[i]["Driver"] == final_laps.iloc[j]["Driver"]:

                #if the session is free practice 1, it will save the data from fp1 and add it under the fp1 columns
                if final_laps.iloc[j]["Session"] == "FP1":
                    fp1_time = final_laps.iloc[j]["LapTime"]
                    fp1_position = final_laps.iloc[j]["Position"]

                    final_laps.loc[i, "FP1 Lap Time"] = fp1_time
                    final_laps.loc[i, "FP1 Position"] = fp1_position

                #if the session is free practice 2, it will save the data from fp2 and add it under the fp2 columns
                elif final_laps.iloc[j]["Session"] == "FP2":
                    fp2_time = final_laps.iloc[j]["LapTime"]
                    fp2_position = final_laps.iloc[j]["Position"]

                    final_laps.loc[i, "FP2 Lap Time"] = fp2_time
                    final_laps.loc[i, "FP2 Position"] = fp2_position

                #if the session is free practice 3, it will save the data from fp3 and add it under the fp3 columns
                elif final_laps.iloc[j]["Session"] == "FP3":
                    fp3_time = final_laps.iloc[j]["LapTime"]
                    fp3_position = final_laps.iloc[j]["Position"]

                    final_laps.loc[i, "FP3 Lap Time"] = fp3_time
                    final_laps.loc[i, "FP3 Position"] = fp3_position

                #if the session is qualifying, it will save the data from it and add it under the qualifying columns
                elif final_laps.iloc[j]["Session"] == "Q":
                    q_time = final_laps.iloc[j]["LapTime"]
                    q_position = final_laps.iloc[j]["Position"]

                    final_laps.loc[i, "Qualifying Lap Time"] = q_time
                    final_laps.loc[i, "Qualifying Position"] = q_position

        #this takes the final results data and saves that to the race data on the final laps page
        for k in range(len(final_results)):
            #if the drivers are the same, it will save their position and add it to the final laps dataset
            if final_laps.iloc[i]["Driver"] == final_results.iloc[k]["Abbreviation"]:
                    r_position = final_results.iloc[k]["Position"]
                    final_laps.loc[i, "Race Position"] = r_position

    #resets the row numbers
    final_laps = final_laps.reset_index(drop = True)

    #deletes all the rows except for the first twenty (those have all the data we need, the rest we dont need)
    for i in range(20, len(final_laps)):
        while True:
            #uses try and accept for when it gets to the last driver and theres no line of that number
            try:
                final_laps = final_laps.drop(index = i)
                final_laps = final_laps.reset_index(drop = True) 
            #if the index is out of bounds, the while loop will break
            except KeyError:
                break
    
    #this deletes the columns I needed for organizing data but do not need for the actual dataset
    final_laps = final_laps[[c for c in later_keep_cols if c in final_laps.columns]]
    

    #if the location is Bahrain, it will add the new dataset to a new variable indicating that its Bahrain (this will
    #be used for the csv file later)
    if l == "Bahrain":
        bahrain_final_laps = final_laps
        bahrain_final_results = final_results
    #if the location is Miami, it will add the new dataset to a new variable indicating that its Miami (this will
    #be used for the csv file later)
    elif l == "Miami":
        miami_final_laps = final_laps
        miami_final_results = final_results
    #if the location is Monaco, it will add the new dataset to a new variable indicating that its Monaco (this will
    #be used for the csv file later)
    elif l == "Monaco":
        monaco_final_laps = final_laps
        monaco_final_results = final_results
    #if the location is Spain, it will add the new dataset to a new variable indicating that its Spain (this will
    #be used for the csv file later)
    elif l == "Spain":
        spain_final_laps = final_laps
        spain_final_results = final_results


#converts the final laps and results lists from each race into a csv file
bahrain_final_laps.to_csv("CHANGE_ME", index = False)
bahrain_final_results.to_csv("CHANGE_ME", index = False)
miami_final_laps.to_csv("CHANGE_ME", index = False)
miami_final_results.to_csv("CHANGE_ME", index = False)
monaco_final_laps.to_csv("CHANGE_ME", index = False)
monaco_final_results.to_csv("CHANGE_ME", index = False)
spain_final_laps.to_csv("CHANGE_ME", index = False)
spain_final_results.to_csv("CHANGE_ME", index = False)

#reads the data from each csv file (above) so that it can be combined
bahraincsv = pd.read_csv("CHANGE_ME")
miamicsv = pd.read_csv("CHANGE_ME")
monacocsv = pd.read_csv("CHANGE_ME")
spaincsv = pd.read_csv("CHANGE_ME")

#combines all the data from the csv files (directly above) and creates a new csv file from it
combined = pd.concat([bahraincsv, miamicsv, monacocsv, spaincsv], ignore_index = True)
combined.to_csv("CHANGE_ME", index = False)

#prints that the dataset was created
print("Dataset Created!")
