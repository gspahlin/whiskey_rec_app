import PySimpleGUI as sg
import psycopg2
import pandas as pd

def s_query(phrase:str) ->str:
    '''Returns a string that is a runnable SQL query on the whiskey db'''

    q_string = f'''
    SELECT whiskey_stats.name,  clusters.clustering
    FROM whiskey_stats
    INNER JOIN clusters
    ON whiskey_stats.whiskey_id = clusters.whiskey_id
    WHERE whiskey_stats.name LIKE '%{phrase}%'
    '''
    return q_string



def main():
    #start connection
    con = psycopg2.connect('dbname=WhiskyAdvocate user= postgres password = 23Tiafdtd32 host = 127.0.0.1 port = 5432')

    #layout 

    search_element = [
        [sg.Text('Whisky Search')],
        [sg.InputText(key = '-WS-')],
        [sg.Button('Search')]
    ]

    s_return = [
        [sg.Text('Whiskys Found')],
        [sg.Listbox(values = [], size = (40, 20), key = '-WF-')]
    ]

    layout = [search_element, s_return]
    window = sg.Window('Whisky Recommender', layout, resizable = True)

    #event loop
    #create event loop 
    while True:
        event, values = window.read()
        
        if event == 'Search':
            ws_quer = s_query(values['-WS-'])
            results = pd.read_sql(ws_quer, con)
            w_names = results['name'].to_list()
            window['-WF-'].update(w_names)
           

                
        if event== sg.WIN_CLOSED:
            #this command breaks the loop
            break
    
    #this command closes the Window that I've stored in the window variable
    window.close()

if __name__ == '__main__':
    main()