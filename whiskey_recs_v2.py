import PySimpleGUI as sg
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as fct

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
    SELECT whiskey_stats.name, whiskey_stats.score, clusters.clustering, reviews.review, features_rev.*
    FROM whiskey_stats
    INNER JOIN clusters
    ON whiskey_stats.whiskey_id = clusters.whiskey_id
    INNER JOIN reviews
    ON whiskey_stats.whiskey_id = reviews.whiskey_id
    INNER JOIN features_rev
    ON whiskey_stats.whiskey_id = features_rev.whiskey_id
    WHERE clusters.clustering = {cluster_num}
    '''
    return c_string

def feature_graph(wd_cts_lst:list) -> object:
    plt.cla()
    plt.figure(figsize = (8, 8))
    features = ['Fruity Words', 'Wood Words', 'Spicy Words', 'Sweet Word', 'Maillard Words', 'Smoke Words']
    plt.bar(features, wd_cts_lst)
    plt.title('Descriptive Language in Review')
    plt.xlabel('Word Types')
    plt.ylabel('Counts')
    return plt.gcf()

def draw_feature_graph(canvas:object, figure:object) -> object:
    figure_canvas_agg = fct(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side = 'top', fill = 'both', expand = 1)
    return figure_canvas_agg


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
        [sg.Listbox(values = [], size = (60, 40), enable_events = True, key = '-WF-')]
    ]

    c_return = [
        [sg.Text('Cluster Mates:')],
        [sg.Listbox(values = [], size = (60, 40), enable_events = True, key = '-CF-')]

    ]
    rev_return = [
        [sg.Text('Score')],
        [sg.Text("", size = (5, 5), enable_events = True, key = '-SCR-')],
        [sg.Text('Review:')],
        [sg.Text("", size = (40, 20), enable_events = True, key = '-REV-')],
        [sg.Text("Review Analysis")],
        [sg.Graph(canvas_size = (10, 10), graph_bottom_left = (0,0), graph_top_right = (10, 10), key = '-Feats-')] #size = (20, 20),
    ]

    layout = [[search_element, sg.Column(s_return), sg.Column(c_return), sg.VSeparator(), sg.Column(rev_return)]]
    window = sg.Window('Whisky Recommender', layout, finalize = True, resizable = True)

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
            #get data by running the query
            c_res = pd.read_sql(c_q, con)
            #unpack into lists
            c_names = c_res['name'].to_list()
            c_revs = c_res['review'].to_list()
            c_score = c_res['score'].to_list()

            # divise containement for flavor data here:
            fruit_words = c_res['fruity_words'].to_list()
            wood_words = c_res['wood_words'].to_list()
            spicy_words = c_res['spicy_words'].to_list()
            sweet_words = c_res['sweet_words'].to_list()
            maillard_words = c_res['maillard_words'].to_list()
            smoke_words = c_res['smoke_words'].to_list()

            #pack a feature dict
            feature_dict = {}

            for a,b,c,d,e,f,g in zip(c_names, fruit_words, wood_words, spicy_words, sweet_words, maillard_words, smoke_words):
                fill_list = [b,c,d,e,f,g]
                feature_dict.update({a:fill_list})

            #organize scores and reviews with dictionaries for easy access 
            rev_dict = {}
            for n, r in zip(c_names, c_revs):
                rev_dict.update({n:r})

            score_dict = {} 
            for n, s in zip(c_names, c_score):
                score_dict.update({n:s})

            #update the window with the names of the whiskeys in the cluster
            window['-CF-'].update(c_names) 

        elif event =='-CF-':
            scr_val = score_dict[values['-CF-'][0]]
            scr_val = str(scr_val)
            rev_val = rev_dict[values['-CF-'][0]]
            feature_val = feature_dict[values['-CF-'][0]]
            feature_fig = feature_graph(feature_val)
            draw_feature_graph(window['-Feats-'].TKCanvas, feature_fig)
            window['-SCR-'].update(scr_val)
            window['-REV-'].update(rev_val)         

                
        if event== sg.WIN_CLOSED:
            #this command breaks the loop
            break
    
    #this command closes the Window that I've stored in the window variable
    window.close()

if __name__ == '__main__':
    main()