import sys
import copy
import csv
import warnings
import os
import math

class ImputerApi(object):
    def __init__(self, path_to_file=None, matrix_2D=None, delimiter=",", strategy="mean",headers=True) -> None:
        """
        Constructor
        Return : None
        """
        self.path_to_file = path_to_file
        self.matrix_2D = matrix_2D
        self.delimiter = delimiter
        self.strategy = strategy
        self.data = []
        self.headers = headers
        self.headers_value = []
        self.supported_strategies = ["mean","median","most-frequent","constant"]
        if self.strategy not in self.supported_strategies:
            print(f":ERROR: `{self.strategy}` is not a supported strategy.\nSupported strategies are: `{('`,`'.join(self.supported_strategies))}` .")
            sys.exit(1)
        if self.path_to_file == None and matrix_2D == None:
            print(f":ERROR: Please provide either a csv file or a two dimensional matrix.")
            sys.exit(1)
        if self.path_to_file != None and matrix_2D != None:
            print(f":ERROR: Please provide either a csv file or a two dimensional matrix.")
            sys.exit(1)
        if matrix_2D != None and isinstance(self.matrix_2D,list)==False:
            print(f":ERROR: `matrix_2D` attribute must be a two dimensional matrix.")
            sys.exit(1)
        if self.path_to_file != None:
            self.prepare_data()
        if self.matrix_2D !=None:
            if self.headers == True:
                self.headers_value = self.matrix_2D[0]
                self.data = copy.deepcopy(self.matrix_2D[1:])
            else:
                self.data = copy.deepcopy(self.matrix_2D)

    @staticmethod
    def not_implemented(fn_name):
        """Helper Function

            Parameters:
            fn_name (string): Function Name

            Returns:
            None

        """
        print(f"\n`{fn_name}` is not implemented yet.\n\n")
        raise NotImplementedError
    
    @staticmethod
    def give_me_first(arr):
        """Function to get first element of a list and the rest
        
            Parameters:
            arr (List): Input List

            Returns:
            Tuple: (First Element, Rest of the List)

        """
        # Not exactly pop but loose
        if isinstance(arr,list)==False:
            raise Exception("InvalidType")
        if len(arr) == 0:
            raise Exception("EmptyList")
        new_arr = arr[1:]
        return arr[0], new_arr


    def prepare_data(self):
        data_arr = []
        try:
            with open(self.path_to_file) as csvreader:
                data=csv.reader(csvreader,delimiter=self.delimiter)
                for row in data:
                    data_arr.append([x for x in row])
            csvreader.close()
            if self.headers==True:
                self.headers_value = data_arr[0]
                if '' in self.headers_value:
                    warnings.warn(":WARNING: Header contains blank value.")
                self.data = copy.deepcopy(data_arr[1:])
            else:
                self.data = copy.deepcopy(data_arr)

        except Exception as e:
            print(e)
            print(e.args)
            sys.exit(1)
    
    def transform(self,columns_by_header_name=[],column_indexes=[],row_start=0,row_end=-1,missing_value='',constant=None):
        if row_end==-1:
            row_end = len(self.data)-1
        if isinstance(row_start,int)==False or row_start<0 or row_start>row_end or (float(row_start)-row_start)!=0.0:
            print(f":ERROR: `row_start` must be an integer between 0 and {len(self.data)-1}.")
            sys.exit(1)
        if isinstance(row_end,int)==False or row_end<0 or row_end>len(self.data)-1 or (float(row_end)-row_end)!=0.0:
            print(f":ERROR: `row_end` must be an integer between 0 and {len(self.data)-1}.")
            sys.exit(1)
        if len(columns_by_header_name) == 0 and len(column_indexes) == 0:
            columns_by_header_name = self.headers_value if len(self.headers_value)>0 else []
        
        col_header_indexes = self.transform_sub_1(columns_by_header_name,column_indexes)
        # print(col_header_indexes)
        
        fn_mapping={
            "mean": self.arr_replace_by_mean,
            "median": self.arr_replace_by_median,
            "most-frequent":self.arr_replace_by_most_frequent,
            "constant":self.arr_replace_by_constant
        }
        fn_to_be_called = fn_mapping[self.strategy]
        if isinstance(missing_value,list):
            missing_value = list(set(missing_value))
        result=[]
        for index in col_header_indexes:
            temp_array=[]
            for i in range(row_start,row_end+1):
                temp_array.append(self.data[i][index])
            if isinstance(missing_value,list)==True:
                if True in [math.isnan(x) for x in missing_value]:
                    index_arr = [i for i in range(0,len(temp_array)) if temp_array[i] in missing_value or math.isnan(temp_array[i])]
                else:
                    index_arr = [i for i in range(0,len(temp_array)) if temp_array[i] in missing_value]
            else:
                if isinstance(missing_value,str):
                    index_arr = [i for i in range(0,len(temp_array)) if temp_array[i] == missing_value]
                else:
                    if math.isnan(missing_value):
                        index_arr = [i for i in range(0,len(temp_array)) if math.isnan(temp_array[i]) == True]
            if index_arr == []:
                warning_text = f":WARNING: There are no missing value = ` {missing_value} ` in the given range from {row_start} to {row_end} and in selected columns: {col_header_indexes} .\n"
                warnings.warn(warning_text)
            if self.strategy == "constant":
                if constant==None:
                    print(f"\n:ERROR: Parameter `constant` needs to be passed to `transform`.\n")
                    sys.exit(1)
                else:
                    result.append(fn_to_be_called(temp_array,index_arr,missing_value,constant))
            else:
                result.append(fn_to_be_called(temp_array,index_arr,missing_value))
                
        return self.transform_sub_2_put_back(row_start,row_end,col_header_indexes,result)

    def transform_sub_1(self,columns_by_header_name,column_indexes):
        col_header_indexes=[]
        not_found_fr_dbgn=[]
        for i in range(0,len(columns_by_header_name)):
            if columns_by_header_name[i] not in self.headers_value:
                not_found_fr_dbgn.append(columns_by_header_name[i])
            else:
                for j in range(0,len(self.headers_value)):
                    if columns_by_header_name[i]==self.headers_value[j]:
                        col_header_indexes.append(j)
            
        if len(col_header_indexes) == 0 and len(not_found_fr_dbgn)>0:
            print(f"\n:ERROR: Invalid column names: `{'`, `'.join(not_found_fr_dbgn)}`.\n")
            raise Exception("InvalidColumnName")
        if len(col_header_indexes)>0 and len(not_found_fr_dbgn)>0:
            print(f"\n:ERROR: Invalid column names: `{'`, `'.join(not_found_fr_dbgn)}`.\n")
            raise Exception("InvalidColumnName")
        
        if len(col_header_indexes)==len(self.data[0]):
            pass
        elif len(column_indexes)>len(self.data[0]):
            print(f'\n:ERROR: (Number of columns to be selected should be less than or equal to total number of columns in the data(= {len(self.data[0])} ).\n')
            raise Exception("LengthMismatch")
        else:
            for el in column_indexes:
                if isinstance(el,int)==False or el<0 or el >= len(self.data[0]) or float(el)-el!=0.0:
                    print(f"\n:ERROR: Invalid index value: `{el}`. Index must be an integer between 0 and {len(self.data[0])-1}. Total Number of columns in the data = {len(self.data[0])}. \n")
                    raise ValueError
                col_header_indexes.append(el)
        
        col_header_indexes=list(set(col_header_indexes))
        return col_header_indexes

    def transform_sub_2_put_back(self,row_start,row_end,col_header_indexes,result):
        assert(len(col_header_indexes)==len(result))
        data_copy = copy.deepcopy(self.data)
        for j in col_header_indexes:
            arr,new_arr=ImputerApi.give_me_first(result)
            result = copy.deepcopy(new_arr)
            for i in range(row_start,row_end+1): 
                el,rest = ImputerApi.give_me_first(arr)
                arr=rest
                data_copy[i][j] = el

            if new_arr==[]:
                return data_copy
        
    def print_table(self,arr_2D,row_sep=" "):
        assert(isinstance(arr_2D,list))
        assert(len(arr_2D)>0)
        header_dashes_chars_count = len(''.join([str(x) for x in arr_2D[0]])) + len(arr_2D[0])
        if self.headers_value != []:
            if (len(''.join(self.headers_value)) + len(self.headers_value)) > header_dashes_chars_count:
                header_dashes_chars_count = len(''.join(self.headers_value)) + len(self.headers_value)
            print("-"*header_dashes_chars_count)  
            print(row_sep.join(self.headers_value))
        else:
            print('-'*header_dashes_chars_count)
        for row in arr_2D:
            print(row_sep.join([str(x) for x in row]))
        print('-'*header_dashes_chars_count)

    def dump_data_to_csv(self,dst_file_path,data:list,delimiter=',',quotechar='"',override=False,use_header_from_data=False):
        """Function to get mean of a list 
        
            Parameters:
            dst_file_path (String): CSV file name to write to,
            data (List): Matrix to be written,
            delimiter (String): Delimiter to be used in CSV,
            quotechar (Strng): Quote Character to be used while wrting to CSV,
            override (Boolean): Override existing file,
            use_header_from_data (Boolean): Flag whether to use header values from input data

            Returns:
            None

        """
        assert(dst_file_path!='' or dst_file_path!=None)
        if (dst_file_path.split("."))[-1] == dst_file_path:
            dst_file_path = dst_file_path+".csv"
        if (dst_file_path.split("."))[-1] != 'csv':
            print("\n:ERROR: Extension of file must be .csv\n")
            raise Exception("InvalidFileExtension")
        if os.path.exists(dst_file_path):
            if override == False:
                print(f"\n:ERROR: FilePath : `{dst_file_path}` already exists. Use override=True in dump_data_to_csv function. \n")
                sys.exit(1)
            else:
                pass
        try:
            with open(dst_file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=delimiter,quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)
                if use_header_from_data == True:
                    if self.headers_value == []:
                        warnings.warn("\n:WARNING: Original Data File have no header values. Skipping use_header_from_data=True flag\n")
                    else:
                        csv_writer.writerow(self.headers_value)

                for row in data:
                    csv_writer.writerow(row)
            csvfile.close()
        except Exception as e:
            print(e)
            print("\n:ERROR: Error while writing to file.\n")
            sys.exit(1)

        print(f"\nFile Saved: `{dst_file_path}`")

    @staticmethod
    def mean(arr,missing_value=''):
        """Function to get mean of a list 
        
            Parameters:
            arr (List): Input List,
            missing_value (Any): Value to be skipped

            Returns:
            float: Mean of the List

        """
        l = len(arr)
        missing_count=0
        nan_flg=False
        if isinstance(missing_value,list):
            for x in missing_value:
                if isinstance(x,str)==False:
                    if math.isnan(x)==True:
                        nan_flg = True
                        break
        else:
            if isinstance(missing_value,str)==False:
                if math.isnan(missing_value) == True:
                    nan_flg = True
        try:
            assert(l > 0)
        except Exception as e:
            print(f":ERROR: Empty List.")
            sys.exit(1)
        sum = 0
        for i in range(l):
            miss_flg = False
            if nan_flg == True:
                if isinstance(missing_value,list):
                    for x in missing_value:
                        if math.isnan(x) == True:
                            if math.isnan(arr[i]) == True:
                                missing_count = missing_count + 1
                                miss_flg = True
                        if math.isnan(x) == False :
                            if arr[i] == x:
                                missing_count = missing_count + 1
                                miss_flg = True
                                continue
                else:
                    if math.isnan(arr[i]):
                        missing_count = missing_count + 1
                        miss_flg = True
                        continue
            if nan_flg == False:
                if arr[i] == missing_value or arr[i] in missing_value:
                    missing_count = missing_count + 1
                    miss_flg = True
                    continue
            if miss_flg==False:
                try:
                    sum = sum + float(arr[i])
                except Exception as e:
                    print(e)
                    print(
                        f":ERROR: Conversion of `{arr[i]}` to float failed at array location `{i}`.")
                    print("Strategy `mean` requires values to be float.")
                    print(f"If `{arr[i]}` is a missing value, pass multiple values in missing_value=[...,'{arr[i]}'] as a List value in parameter of transform function.")
                    sys.exit(1)
        
        return (sum/(l-missing_count))

    @staticmethod
    def median(arr,missing_value=''):
        """Function to get median of a list 
        
            Parameters:
            arr (List): Input List,
            missing_value (Any): Value to be skipped

            Returns:
            float: median of the List

        """
        l = len(arr)
        nan_flg=False
        if isinstance(missing_value,list):
            for x in missing_value:
                if isinstance(x,str) == False:
                    if math.isnan(x)==True:
                        nan_flg = True
                        break
        else:
            if isinstance(missing_value,str) == False:
                if math.isnan(missing_value) == True:
                    nan_flg = True
        try:
            assert(l > 0)
        except Exception as e:
            print(f":ERROR: Empty List.")
            sys.exit(1)
        arr_cp=[]
        arr_gen=(x for x in arr)
        for i in range(l):
            try:
                el = next(arr_gen)
                if nan_flg == True:
                    if math.isnan(el):
                        continue
                if el == missing_value or el in missing_value:
                    pass
                else:
                    arr_cp.append(float(el))
            except Exception as e:
                print(e)
                print(
                    f":ERROR: Conversion of `{el}` to float failed at array location `{i}`.")
                print(f"Strategy `median` requires values to be float.") 
                print(f"If `{el}` is a missing value, pass multiple values in missing_value=[...,'{el}'] as a List value in parameter of transform function.")
                sys.exit(1)
        arr_cp = sorted(arr_cp)
        if len(arr_cp) % 2==1:
            return arr_cp[len(arr_cp)//2]
        else:
            return (arr_cp[len(arr_cp)//2]+arr_cp[len(arr_cp)//2-1])/2
    
    @staticmethod
    def most_frequent(arr,missing_value=''):
        """Function to get most frequent value of a list 
        
            Parameters:
            arr (List): Input List,
            missing_value (Any): Value to be skipped

            Returns:
            any: most frequent value of the List

        """
        try:
            assert(len(arr)>0)
        except Exception as e:
            print(e)
            print(":ERROR: Empty List.")
            sys.exit(1)
        nan_flg=False
        if isinstance(missing_value,list):
            for x in missing_value:
                if isinstance(x,str) == False:
                    if math.isnan(x)==True:
                        nan_flg = True
                        break
        else:
            if isinstance(missing_value,str) == False:
                if math.isnan(missing_value) == True:
                    nan_flg = True
        dct = {}
        for el in arr:
            if nan_flg == True:
                if math.isnan(el):
                    continue
            if isinstance(missing_value,list):
                if el in missing_value:
                    pass
            if el == missing_value:
                pass
            else:
                if str(el) in dct.keys():
                    dct[str(el)] = dct[str(el)] + 1
                else:
                    dct[str(el)] = 1
        max_key = ''
        max_val = 0
        for (k,v) in dct.items():
            if v > max_val:
                max_val = v
                max_key = k
        return max_key

    @staticmethod
    def euclidian_distance_2d(tup1,tup2):
        assert(isinstance(tup1) == tuple)
        assert(isinstance(tup2) == tuple)
        assert(len(tup1) == 2)
        assert(len(tup2) == 2)

        x1,y1 = tup1
        x2,y2 = tup2
        return math.sqrt((x2-x1)**2+(y1-y2)**2)

    @staticmethod
    def levenshteinDistance(s1, s2):
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]


    def arr_replace_by_mean(self, arr, index_arr,missing_value=''):
        """Wrapper Function over mean which performs replace operation given indexed array 
        
            Parameters:
            arr (List): Input List,
            index_arr (List:Int):  Indexes of list whose values are to be replaced,
            missing_value (Any): Value to be skipped

            Returns:
            list: Replaced List

        """
        arr_copy = copy.deepcopy(arr)
        mean_ = ImputerApi.mean(arr_copy,missing_value)
        for i in index_arr:
            if isinstance(arr[i],str):
                arr_copy[i] = str(mean_)
            else:
                arr_copy[i] = mean_
        return arr_copy

    def arr_replace_by_median(self, arr, index_arr,missing_value=''):
        """Wrapper Function over median which performs replace operation given indexed array 
        
            Parameters:
            arr (List): Input List,
            index_arr (List:Int):  Indexes of list whose values are to be replaced,
            missing_value (Any): Value to be skipped

            Returns:
            list: Replaced List

        """
        arr_copy = copy.deepcopy(arr)
        median_ = ImputerApi.median(arr_copy,missing_value)
        for i in index_arr:
            if isinstance(arr[i],str):
                arr_copy[i] = str(median_)
            else:
                arr_copy[i] = median_
        return arr_copy

    def arr_replace_by_most_frequent(self, arr, index_arr,missing_value=''):
        """Wrapper Function over most_frequent which performs replace operation given indexed array 
        
            Parameters:
            arr (List): Input List,
            index_arr (List:Int):  Indexes of list whose values are to be replaced,
            missing_value (Any): Value to be skipped

            Returns:
            list: Replaced List

        """
        arr_copy = copy.deepcopy(arr)
        most_frequent_ = ImputerApi.most_frequent(arr_copy,missing_value)
        for i in index_arr:
            if isinstance(arr[i],str):
                arr_copy[i] = str(most_frequent_)
            else:
                arr_copy[i] = most_frequent_
        return arr_copy
    
    def arr_replace_by_constant(self, arr, index_arr,missing_value='',constant=''):
        """Wrapper Function which performs replace operation given indexed array and a constant
        
            Parameters:
            arr (List): Input List,
            index_arr (List:Int):  Indexes of list whose values are to be replaced,
            missing_value (Any): Value to be skipped,
            constant (Any): Value to be replaced with

            Returns:
            list: Replaced List

        """
        arr_copy = copy.deepcopy(arr)
        for i in index_arr:
            if isinstance(arr[i],str):
                arr_copy[i] = str(constant)
            else:
                arr_copy[i] = constant
        return arr_copy
