import json
import os

def merge_json(file1, file2):
    
    with open("merge_result_new.json", "w", encoding="utf-8") as outfile:
        with open(file1, "r", encoding="utf-8") as infile:
            data1 = json.load(infile)
        with open(file2, "r", encoding="utf-8") as infile:
            data2 = json.load(infile)

        for cur in data2:
            if cur not in data1:
                data1.append(cur)
        
        print(len(data1))
        json.dump(data1, outfile, ensure_ascii=False, indent=4)

def merge_http(file1):
    
    base_url = "https://www.foody.vn/"
    with open("merge_result.json", "w", encoding="utf-8") as outfile:
        with open(file1, "r", encoding="utf-8") as infile:
            data = json.load(infile)

        result = []
        for cur in data:
            complete_link = base_url + cur
            if complete_link not in result:
                result.append(complete_link)
        
        print(len(result))
        json.dump(result, outfile, ensure_ascii=False, indent=4)

merge_http("merge_result_new.json")
# merge_json("merge_result.json", "foodcourt.json")