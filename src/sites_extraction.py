import pandas
import argparse
from pathlib import Path
from pyproj import Geod

def secondary_enodeb_filter(element, dataframe, geod):

    # apply passess the row as a Series so the index becomes the name attribute
    limit = 1
    index = element.name + 1
    pos_el = (element['cell_long'], element['cell_lat'])

    for row in dataframe.iloc[index:].itertuples():
        pos_row = (row[4], row[3])
        _, _, dist = geod.inv(pos_el[0], pos_el[1], pos_row[0], pos_row[1], return_back_azimuth=True)
        if dist <= limit:
            return False
    return True


def extraction(input_path, output_file, city_name):
    """ Extracts cell sites of a city from an input file and writes them into
    a new file. 

    Parameters
    ----------
    input_file : string
        Input file path.
    output_file : string
        Output file path.
    city_name : string
        City name to filter the sites.
    """
    
    g = Geod(ellps='WGS84')

    col_list = ['node_id', 'cell_lat', 'cell_long', 'site_name']
    
    df = pandas.read_csv(input_path, sep=";", usecols=col_list)

    # filters the dataframe to keep only the sites of the specified city
    turin_cells = df[df['site_name'].str.startswith(city_name, na=False)]

    # filters the cells to keep only one per site
    cell_sites = turin_cells.drop_duplicates(subset=['node_id'])
   
    cell_sites.reset_index(drop=True, inplace=True)

    cell_sites = cell_sites[cell_sites.apply(secondary_enodeb_filter, axis=1, args=(cell_sites,g))]
    
    # reordering of the columns in order of importance
    cell_sites = cell_sites[['node_id', 'cell_lat', 'cell_long', 'site_name']]

    cell_sites.rename(columns={'cell_lat': 'site_lat', 'cell_long': 'site_long'},
                      inplace=True)

    cell_sites.to_csv(output_file, mode='w',  index=False)

def main():
    """ Handles the command line arguments and calls the extraction function 
    with their values.
    """
    
    parser = argparse.ArgumentParser(description="file that extracts from an "
                                    "input file the cell sites of a certain" 
                                    "city and writes to a new file the node id, "
                                    " latitude, longitude and site name.")
    parser.add_argument('-i', '--input', required=True, help="the file path "
                        "from which the sites will be extracted.")
    parser.add_argument('-o', '--output', default='output_sites.csv', help="the file path "
                        "on which the extracted sites will be written.")
    parser.add_argument('-c', '--city', required=True, help="the city name to filter the input file.")
    args = parser.parse_args()

    # checks the output file path and creates missing directories
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True, parents=True)

    extraction(args.input, args.output, args.city)

if __name__ == '__main__':
    main()
