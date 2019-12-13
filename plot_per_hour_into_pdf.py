import pandas as pd # pandas for data manipulation
from datetime import datetime # datetime to convert the timestamp

filename = "" # name of the file here. !!! dont forget the format .csv !!!
            # !!! will throw an error otherwise!!!
y_lim = 0.3 # limit the values shown on the y-axis
output_format = ".pdf" # put format in here

# data section
data = pd.read_csv(filename,header=None,names=['timestamp','Vals'])  # reading the data


# sort the data
data['miliseconds'] = data['Vals'].apply(lambda x: int(x.split(' ')[0])*10)
data['amplitude'] = data['Vals'].apply(lambda x: int(x.split(' ')[-1]))


# get datetime data
data['datetime'] = data['timestamp'].apply(lambda x: datetime.utcfromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))
data['year'] = data['datetime'].apply(lambda x: int(x.split(' ')[0].split('-')[0]))
data['month'] = data['datetime'].apply(lambda x: int(x.split(' ')[0].split('-')[1]))
data['day'] = data['datetime'].apply(lambda x: int(x.split(' ')[0].split('-')[2]))
data['hour'] = data['datetime'].apply(lambda x: int(x.split(' ')[1].split(':')[0]))
data['minute'] = data['datetime'].apply(lambda x: int(x.split(' ')[1].split(':')[1]))
data['second'] = data['datetime'].apply(lambda x: int(x.split(' ')[1].split(':')[2]))

# remove timestamp and the raw data.
data = data.drop("Vals", axis=1)
data = data.drop("timestamp", axis=1)

# maximum norming
maximum = data['amplitude'].max()
minimum = data['amplitude'].min()
unsigned_minimum = (minimum**2)**(1/2.0) # squared and then root **(1/2.0) <-- has to be written this way in pyhon appearently
if(maximum>=unsigned_minimum):
    data['normed_amplitude'] = data['amplitude'].apply(lambda x: x/maximum)
else:
    data['normed_amplitude'] = data['amplitude'].apply(lambda x: x/unsigned_minimum)

# make a time value that lets us sort the values over minutes, seconds and miliseconds. decomplicates the plotting loops a smidge
data['time_unifyer'] = data['minute']/(60/100)*10000 + data['second']/(60/100)*100 + data['miliseconds']/10
data['time_unifyer'] = data['time_unifyer'].apply(lambda x: x/1000000 * 60)

# plotting seciton
import matplotlib.pyplot as plt # matplotlib for plotting (surprise!!)

for year in range(data['year'].min(),data['year'].max()+1):
    data_year = data[data['year']==year]
    
    for month in range(data_year['month'].min(),data_year['month'].max()+1):
        data_month = data_year[data_year['month']==month]
        
        for day in range(data_month['day'].min(),data_month['day'].max()+1):
            data_day = data_month[data['day']==day]

            hour_min = data['hour'].min()
            hour_max = data['hour'].max()
            nrow = hour_max - hour_min
            ncol = 1
            current_hour = hour_min
            fig, axs = plt.subplots(nrows=nrow, ncols=ncol,sharex=True,sharey=True,figsize=(8.27,11.69))

            for ax in axs.flat:
                df = data[(data['hour']==current_hour)]
                values = df['normed_amplitude'].data
                time = df['time_unifyer'].data
                ax.set_yticklabels([])

                ax.set_ylabel(str(current_hour))
                ax.plot(time,values)

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
                
                current_hour+=1

            #fig.patch.set_visible(False)
            fig.text(0.52, 0.033, 'minutes', ha = 'center')
            fig.text(0, 0.35, 'graph of the respective hour of the maximum norm of values', ha= 'center', rotation='vertical')            
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            fig.suptitle(f"seismometer graphs of {day}/{month}/{year} per hour", fontsize=14)
            plt.xlim(0, 60, 5)
            plt.ylim(y_lim*(-1),y_lim)
            file_name = f"seismometer_plot_{year}_{month}_{day}_limited_by_{int(y_lim*100)}%_max_value{output_format}"
            fig.savefig(fname = file_name)