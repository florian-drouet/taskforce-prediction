import pandas as pd
import datetime
import os
import numpy as np
import pickle
import psycopg2

def pgsql_connector(DEBUG):
    if DEBUG:
        host = "localhost"
        port = 5432
        dbname = "postgres"
        user = "postgres"
        password = '1ntothew1ld!'
        conn = psycopg2.connect(f'postgresql://{user}:{password}@{host}:{port}/{dbname}')
    else:
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print("### Connection to pgSQL successful ! ###")
    return conn

def get_data(DEBUG):
    #Connect to pgSQL database
    pgsql_connection = pgsql_connector(DEBUG)
    
    #Read data
    df = pd.read_sql_query("""
    SELECT *
    FROM dataset;
    """, con=pgsql_connection, parse_dates=['date_analysis'], index_col=['date_analysis']).sort_index()
    
    variable_nurse = ['time_presence_nurse']
    variable_doctor = ['time_presence_doctor']
    variables = ['number_of_red_alerts', 'number_of_non_treated_red_alerts', 'number_of_orange_alerts', 'number_of_non_treated_orange_alerts', 'weekdays']
    
    if (datetime.date.today() - datetime.timedelta(days=1)) == df.index[-1].date():
        print('### Data already up-to-date ! ###')
    else:
        print('### Data has to be updated ! ###')

    pop_type = dict()
    pop_type['nurse'] = df.loc[:,df.columns.isin(variable_nurse)].squeeze()
    pop_type['doctor'] = df.loc[:,df.columns.isin(variable_doctor)].squeeze()
    
    return df.loc[:,df.columns.isin(variables)], pop_type

def machine_learning_parameters():
    path = os.getcwd()

    scaler = pickle.load(open(path+'/data/scaler.sav', 'rb'))
    model_nurse = pickle.load(open(path+'/data/linear_regression_nurse.sav', 'rb'))
    model_doctor = pickle.load(open(path+'/data/linear_regression_doctor.sav', 'rb'))

    model_dict = dict()
    model_dict['doctor'] = model_doctor
    model_dict['nurse'] = model_nurse
    
    return scaler, model_dict

def get_alert_forecasting(projection_mode, projection_parameter, data_red, data_orange, number_of_days_projections):
    if projection_mode == 'linear':
        for i in range(1, number_of_days_projections+1):
            data_red.append(data_red[i-1]+projection_parameter)
            data_orange.append(data_orange[i-1]+projection_parameter)
    elif projection_mode == 'quadratic':
        for i in range(1, number_of_days_projections+1):
            data_red.append(projection_parameter*data_red[i-1])
            data_orange.append(projection_parameter*data_orange[i-1])
    elif projection_mode == 'exponential':
        for i in range(1, number_of_days_projections+1):
            data_red.append(np.exp(data_red[i-1]))
            data_orange.append(projection_parameter*data_orange[i-1])
    return data_red, data_orange

def update_data(X, y, model, preprocessing, projection_mode, projection_parameter, number_of_days_projections):

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    non_dummy_columns = ['number_of_red_alerts', 'number_of_non_treated_red_alerts', 'number_of_orange_alerts', 'number_of_non_treated_orange_alerts']
    dummy_columns = ['weekdays']
    
    projection = pd.DataFrame(columns=X.columns, index=pd.date_range(start=X.tail(1).index[0], end=X.tail(1).index[0] + datetime.timedelta(days=number_of_days_projections)))
    projection.index.name="date"

    projection.number_of_non_treated_red_alerts=0.
    projection.number_of_non_treated_orange_alerts=0.

    data_red = [X.tail(1)["number_of_red_alerts"][0]]
    data_orange = [X.tail(1)["number_of_orange_alerts"][0]]

    projection.number_of_red_alerts, projection.number_of_orange_alerts = get_alert_forecasting(projection_mode, projection_parameter, data_red, data_orange, number_of_days_projections)

    temp = projection.reset_index()
    temp.weekdays = (temp.date.dt.weekday<=4).map({True:1,False:0})
    projection = temp.set_index('date')

    projection_reset = projection.reset_index(drop=True)
    concat_projection = pd.DataFrame(data=preprocessing.transform(projection_reset.loc[:,projection_reset.columns.isin(non_dummy_columns)]), columns=non_dummy_columns)
    projection_scaled = pd.concat((concat_projection, projection_reset[dummy_columns]), axis=1)

    future = model.predict(projection_scaled)
    
    y_true = y.append(pd.Series([future[0]], index=[X.tail(1).index[0]]))
    y_future = pd.Series(data=future, index=pd.date_range(start=X.tail(1).index[0] + datetime.timedelta(days=0), end=X.tail(1).index[0] + datetime.timedelta(days=number_of_days_projections)))
    alerts = pd.concat([X, projection.loc[projection.index>datetime.datetime.combine(yesterday, datetime.datetime.min.time())]], axis=0)
    
    return y_true, y_future, alerts