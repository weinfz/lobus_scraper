import pandas as pd
from tabulate import tabulate
import os
import glob
import re
import argparse


def get_artist(artist_years):
    """gets just the artist
    """
    try:
        return " (".join(artist_years.split(" (")[:-1])
    except AttributeError:
        return ''
  
def get_size(description): 
    """ get the size from the description
    """
    ## check if string
    if isinstance(description,(str,unicode)):
        ### check if height and length are in the descript
        if 'height: ' in description.lower() or 'length: ' in description.lower():
            try:
                ## get the height and lenght between the parathesis with cm
                ## if they are there
                height = ''
                length = ''
                for line in description.split('/n'):
                    if 'height: ' in line.lower():
                        try:
                            height = re.search(r'\((.*?) cm.*\)',line).group(1).strip(' ')
                        except AttributeError:
                            pass
                    if 'length: ' in line.lower():
                        try:
                            length = re.search(r'\((.*?) cm.*\)',line).group(1).strip(' ')
                        except AttributeError:
                            pass
                return '{height}x{length}'.format(height=height, length=length)
            except:
                print(description)
                pass
            ## elese just grab whats between the parathesis in cm
        try:
            size = re.search(r'\((.*?) cm.*\)',description).group(1).replace(' ','')
            return size
        except AttributeError:
            pass
    
def float_0(string):
    try:
        return float(string)  
    except:
        return 0.0
    
class Counter:
    """ just a greedy method to group all the sizes
    basically just take both smallest then the smallest and the second smalles
     then the second smallest and the smallest then both second smallest ..etc
     if prod would do some sort of optimization problem to ge the best groups
     """
    def __init__(self):
        self.switch = 0
        self.min_1_index = 0
        self.min_2_index = 0
    
    def count(self):
        # pretty much just going (0,0),(1,0),(0,1),(1,1),(2,0),(0,2),(2,1)...etc
        if self.min_1_index > 10 or self.min_2_index > 10:
            raise Exception('got to big')
        if self.min_1_index == self.min_2_index:
            self.min_1_index = 0
            self.min_2_index += 1
            self.switch = 1
        elif self.switch == 1:
            print('switch')
            self. min_1_index, self.min_2_index = self.min_2_index, self.min_1_index
            self.switch = 0
        else:
            if self.min_1_index < self. min_2_index:
                self.min_1_index += 1
            elif self.min_2_index < self.min_1_index:
                self.min_2_index += 1
            self.switch = 1
        return self.min_1_index, self.min_2_index

def get_data():
    """gets the data from the csvs and does some formatting
    """
    ### if prod would just add the data to sql instead of csv
    file_path = os.path.dirname(os.path.abspath(__file__))
    glob_folder = os.path.join(file_path,'..','data','*.csv')
    files = glob.glob(glob_folder)
    df = []
    artists = []
    for f in files:
       d = pd.read_csv(f,index_col=0, encoding='utf-8') 
       d['auction_file'] = f
       d['artist'] = d['artist_years'].apply(get_artist)
       artists.append(pd.unique(d['artist']).tolist())
       df.append(d)
    keep_artists = list(set(artists[0]) & set(artists[1]))
    df = pd.concat(df)
    df = df.loc[df['artist'].isin(keep_artists)]
    df = df.loc[df['artist_years'].notnull()]
    df['size'] = df['description'].apply(get_size)
    df['size1'] = df['size'].apply(lambda x:float_0(x.split('x')[0]))
    df['size2'] = df['size'].apply(lambda x:float_0(x.split('x')[1]))
    df['price'] = [''.join(re.findall("\d+", item)) for item in df['sold_price']]
    ## if prod dont hard code this
    df['month'] = ['nov 2017' if '27400' in x else 'feb 2018' for x in df['auction_file']]
    return df

def print_groups(x_diff, debug):
    df = get_data()
    data = []
    group_data = []
    for artist in pd.unique(df['artist']).tolist():
        objects = df.loc[df['artist'] == artist]
        n_objects = len(objects)
        n_objects_left = n_objects   
        group_no = 0
        while n_objects_left !=0:
            ## right now just grouping the objects in an easy way
            ## if prod would lke to standardize groups 
            ## so the numbers between artist would be more meaningful
            counter = Counter()
            min_1_index, min_2_index = 0,0
            current_min_1 = objects['size1'].nsmallest(min_1_index+1).iat[min_1_index]
            current_min_2 = objects['size2'].nsmallest(min_2_index+1).iat[min_2_index]
            group = {'artist':artist}
            group_dat = {}
            current_group = objects.loc[(objects['size1']>=current_min_1) & (objects['size1']<=current_min_1+2*x_diff)
            & (objects['size2']>=current_min_2) & (objects['size2']<=current_min_2+2*x_diff)]
            while len(current_group)==0:
                min_1_index, min_2_index = counter.count()
                try:
                    current_min_1 = objects['size1'].nsmallest(min_1_index+1).iat[min_1_index]
                    current_min_2 = objects['size2'].nsmallest(min_2_index+1).iat[min_2_index]
                    current_group = objects.loc[(objects['size1']>=current_min_1) & (objects['size1']<=current_min_1+2*x_diff)
                    & (objects['size2']>=current_min_2) & (objects['size2']<=current_min_2+2*x_diff)]
                except:
                    continue
    
            objects = objects.loc[~objects.index.isin(current_group.index)]
            n_objects_left = len(objects)
            nov_avg = current_group['price'].loc[current_group['month'] == 'nov 2017'].mean()
            feb_avg = current_group['price'].loc[current_group['month'] == 'feb 2018'].mean()
            nov_objects = current_group['title'].loc[current_group['month'] == 'nov 2017'].tolist()
            feb_objects = current_group['title'].loc[current_group['month'] == 'feb 2018'].tolist()
            group['Nov. price'] = nov_avg
            group['Feb. price'] = feb_avg
            group['group_no'] = group_no
            group_no += 1
            group_dat['Nov. objects'] = nov_objects
            group_dat['Feb. objects'] = feb_objects
            data.append(group)
            group_data.append(group_data)
            
    data = pd.DataFrame(data)
    group_data = pd.DataFrame(group_data)
    ## decided to make debug a variable since the extra data was too much 
    ##to print nicely
    if debug == True:
        print tabulate(group_data, headers='keys', tablefmt='psql', showindex=False)
    print tabulate(data, headers='keys', tablefmt='psql', showindex=False)


def main():

    parser = argparse.ArgumentParser(description="prints the sell vales from similar objects from nov2017 and feb2018")
    parser.add_argument('-tol', '--tolerance', type=float, required=True, help="the range for similar objects", dest='x_diff')
    ## no debugging by default
    parser.add_argument('-d', '--debug', type=bool, default=False, required=False)
    args = parser.parse_args()
    print(args)
    print_groups(args.x_diff, debug=args.debug)
    

if __name__ == "__main__":
    main()
    








