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

def c_query(cluster_num:str) ->str:
    '''Returns a string that is a runnable SQL query on the whiskey db'''

    c_string = f'''
    SELECT whiskey_stats.name, whiskey_stats.score, clusters.clustering, reviews.review
    FROM whiskey_stats
    INNER JOIN clusters
    ON whiskey_stats.whiskey_id = clusters.whiskey_id
    INNER JOIN reviews
    ON whiskey_stats.whiskey_id = reviews.whiskey_id
    WHERE clusters.clustering = {cluster_num}
    '''
    return c_string



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
        [sg.Text('Whiskys Found:')],
        [sg.Listbox(values = [], size = (40, 20), enable_events = True, key = '-WF-')]
    ]

    c_return = [
        [sg.Text('Cluster Mates:')],
        [sg.Listbox(values = [], size = (40, 20), enable_events = True, key = '-CF-')]

    ]
    rev_return = [
        [sg.Text('Review:')],
        [sg.Text("", size = (40, 20), enable_events = True, key = '-REV-')]
    ]

    score_return = [
        [sg.Text('Score')],
        [sg.Text("", size = (5, 5), enable_events = True, key = '-SCR-')]
    ]

    layout = [search_element, s_return, c_return, score_return, rev_return]
    window = sg.Window('Whisky Recommender', layout, resizable = True)

    #event loop
    #create event loop 
    while True:
        event, values = window.read()
        
        if event == 'Search':
            ws_quer = s_query(values['-WS-'])
            results = pd.read_sql(ws_quer, con)
            w_names = results['name'].to_list()
            w_nums = results['clustering'].to_list()
            w_dict = {}
            for n, c in zip(w_names, w_nums):
                w_dict.update({n:c})
            window['-WF-'].update(w_names)

        elif event == '-WF-':
            #values['-WF-'] will return a list with one value: the highlited name
            #the setup below will call the key from the dictionary to get the cluster
            c_val = w_dict[values['-WF-'][0]]
            c_q = c_query(c_val) 
            c_res = pd.read_sql(c_q, con)
            c_names = c_res['name'].to_list()
            c_revs = c_res['review'].to_list()
            c_score = c_res['score'].to_list()
            rev_dict = {}
            for n, r in zip(c_names, c_revs):
                rev_dict.update({n:r})
            score_dict = {} 
            for n, s in zip(c_names, c_score):
                score_dict.update({n:s})
            window['-CF-'].update(c_names) 

        elif event =='-CF-':
            scr_val = score_dict[values['-CF-'][0]]
            scr_val = str(scr_val)
            rev_val = rev_dict[values['-CF-'][0]]
            window['-SCR-'].update(scr_val)
            window['-REV-'].update(rev_val)         

                
        if event== sg.WIN_CLOSED:
            #this command breaks the loop
            break
    
    #this command closes the Window that I've stored in the window variable
    window.close()

if __name__ == '__main__':
    main()