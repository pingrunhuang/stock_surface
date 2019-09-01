import matplotlib as mpl
import numpy as np
import datetime as dt
import pandas as pd
import sample_slopes as sample_slopes
import support_vector as support_vector

plot_bool = 0

tickers = ["AAPL", "MSFT", "GOOG", "FB", "INTC", 'TSM',
           "CSCO", "ORCL", "NVDA", "SAP", "IBM", "ADBE",
           "TXN", "AVGO", "CRM", "QCOM", "MU", "BIDU",
           "ADP", "VMW", "ATVI", "AMAT", "INTU",
           "CTSH", "EA", "NXPI", "INFY", "ADI", "NOK"]
# tickers = ["AAPL", "MSFT", "GOOG"]

start = dt.datetime(2013, 10, 1)
end = dt.datetime(2017, 4, 14)
mpl.rcParams['legend.fontsize'] = 10

# fig = plt.figure(figsize=(8, 8))

# ax = fig.gca(projection='3d')

# style.use('ggplot')

# delta = timedelta(days=1)

# plot_df = pd.DataFrame()

# df2 = pd.DataFrame()


class Ticker_Data():
    """
    object to hold the stock data
    """

    def __init__(self, df):
        self.main_df = df

    def append_change_column(self, df, ticker):
        """
         take the dataframe that holds the stock info and the ticker of interest 
         then append the new change column and the new close column to the main dataframe
        """
        df2 = pd.DataFrame()
        df2['change'] = np.log(df['close']) - np.log(df['close'].shift(1))
        self.main_df[str(ticker) + 'CHG'] = df2['change']
        self.main_df[str(ticker) + 'CLS'] = df['close']
        return self.main_df

    def backTester(self, df):
        for x in range(len(df.columns) - 2):
            df['stock' + str(x + 1)]
            df['stock1compair'] = np.where(df['stock' + str(x + 1)].values < df['stock' + str(x)].values and
                                           df['stock' + str(x + 1)].values < df['stock' + str(x + 2)].values, 1, 0)
        return df

    def drop_row_with_zeros(self):
        """
        removes the rows with zero on teh self.dataframe
        """

        columns = list(self.main_df)

        self.main_df = self.main_df[self.main_df[columns] != 0]

    def drop_row_with_NA(self):
        """
        removes the rows with NA on the self.dataframe
        """

        # self.main_df = self.main_df[self.main_df[columns] != 0]
        self.main_df = self.main_df.dropna()


def write_feature_and_targets(X, Y):
    """
    Takes the X and Y and writest them to a file
    """
    with open('files/testing_files/all_feature.txt', 'w') as file_name:
        for feature in X:
            file_name.write(str(feature) + ',' + '\n')
        for target in Y:
            file_name.write(str(target) + ',' + '\n')


def main(batch_size, look_ahead):
    """
    da main function
    """
    i = 0
    main_df = pd.DataFrame()

    ticker_data = Ticker_Data(main_df)

    # NOTE ============start here to get new stock data=======================

    # for ticker in tickers:
    #     print ticker
    #     time.sleep(.02)
    #     # print ticker
    #     df = web.DataReader(ticker, 'iex', start, end)
    #     df = df.reset_index(level='date')
    #     # print df.head()
    #     ticker_data.append_change_column(df, ticker)

    #     i = i + 50

    # # remove the rows that contain any 0's or NA

    # ticker_data.main_df.to_csv('before_NA_drop_stock_data_slope_sumNoNA' +
    #                            str(start) + '--' + str(end) + '.csv')
    # # ticker_data.drop_row_with_zeros()
    # ticker_data.drop_row_with_NA()

    # ticker_data.main_df.to_pickle(
    #     'stock_data/df_without_NA_' + str(start) + '--' + str(end) + '.pkl')

    # NOTE ============end================================================

    ticker_data.main_df = pd.read_pickle(
        'stock_data/df_without_NA_' + str(start) + '--' + str(end) + '.pkl')

    # add the slope sum values to the dataframe
    # ticker_data.main_df = sample_slopes.create_slope_sum(ticker_data.main_df)

    ticker_data.main_df = sample_slopes.create_slope_sum_market(
        ticker_data.main_df)

    # write the whole datarame to a csv if you want to
    ticker_data.main_df.to_csv(
        'stock_data_slope_sumNoNA' + str(start) + '--' + str(end) + '.csv')

    # get the names of all the column titles
    columns = list(ticker_data.main_df)

    # get the names of the columns that have a slope_sum
    columns_with_sample_slopes = sample_slopes.get_columns_with_slope_sum(
        columns)

    # set up the ML package to hold the features and target values
    sv = support_vector.Support_Vector([], [])

    for column in columns_with_sample_slopes:

        y_values = sample_slopes.generate_target_values(
            ticker_data.main_df, batch_size, column.replace('slope_sum', 'CLS'), look_ahead)
        # keeps adding new target values to varable
        sv.Y = sv.Y + y_values[0]

        # create_batch_of_slopes(df, batch_count, cut_length)
        # y_values[1] bec thats used to tell create batch_of_slopes where to
        # stop

        x_values = sample_slopes.create_batch_of_slopes(
            ticker_data.main_df, column, batch_size,   y_values[1])

        # x_values = sample_slopes.create_batch_of_slopes_moving_av(
        #     ticker_data.main_df, column, batch_size,   y_values[1], 15)

        # keeps adding new feature values to varable
        sv.X = sv.X + x_values

    write_feature_and_targets(sv.X, sv.Y)

    print(sv.Y, 'Yvalues')
    print(sv.X[-1], ' Xvalues ')
    # print sv.X, 'Xvalues'
    print('training the model...')

    sv.train()
    # sv.run_optunity()

    # for sample in test_data:
    #     print sv.predict_out_put([sample])


def iterate_over_all_batch_and_look_ahead():
    """ 
    iterates over all the differnt comindations and writes to a csv file
    """

    for j in range(3, 15):
        for i in range(2, 50):

            sell, buy = main(i, j)

            with open('files/testing_files/hold_percents.txt', 'a')as f:
                f.write(str(float(sell[0]) / float((sell[1] + sell[0]))) + ',' +
                        str(float(buy[1]) / float(buy[1] + buy[0])) +
                        ', ' + str(i) + ',' + str(j) + '\n')
            print(i, j)

if '__main__' == __name__:

    # sell, buy = main(18, 2)
    main(18, 2)

    # start = dt.datetime(2012, 10, 1)
    # end = dt.datetime(2018, 4, 14)
    # ticker = 'HPQ'
    # df = web.DataReader(ticker, 'iex', start, end)
    # print df
    # i = 0
    # arr = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    # while i < (len(arr) - 2 - 1):
    #     print i
    #     i += 1
    # print arr[i], 'hree is '
    # print i
