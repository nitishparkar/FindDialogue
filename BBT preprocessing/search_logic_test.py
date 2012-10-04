import json
import math


"""
  This script was created to test the search logic.
"""


class TestCase():
    """Represents test cases"""
    def __init__(self, id, ip, op):
        self.id = id
        self.ip = ip
        self.op = op


class SearchTerm():
    """Represents search term"""
    word = None
    occurrences = None


def search_logic(model_instances):

    model_instances = [l for l in model_instances if l is not None]

    #print "Initial Lists:"
    #for x in model_instances:
    #    print x.word, ':', x.occurrences
    
    if len(model_instances) < 1:
        print "invlid len"
        return []
    
    meta_list = json.loads(model_instances[0].occurrences)
    for x in meta_list:
        x.append(5)
    
    #print 'ml', meta_list
    for i in range(1, len(model_instances)):
        #print "outer loop i", i
        for occurrence in json.loads(model_instances[i].occurrences):
            #print "inner loop", occurrence
            occurrence.append(5)
            x = 0
            while x < len(meta_list):
                #print 'xmeta:',meta_list
                if meta_list[x][0] == occurrence[0] and meta_list[x][1] == occurrence[1] and meta_list[x][2] == occurrence[2]:
                    meta_list[x][3] += 10
                    break
                if meta_list[x][0] == occurrence[0] and meta_list[x][1] == occurrence[1] and meta_list[x][2] > occurrence[2]:
                    meta_list.insert(x, occurrence)
                    break
                if meta_list[x][0] == occurrence[0] and meta_list[x][1] > occurrence[1]:
                    meta_list.insert(x, occurrence)
                    break
                if meta_list[x][0] > occurrence[0]:
                    meta_list.insert(x, occurrence)
                    break
                x += 1
            else:
                meta_list.append(occurrence)
    #print "Duplicates combined!", meta_list
    valid_words = len(model_instances)
    new_meta_list = []
    combined = False
    for x in range(1, len(meta_list)):
        if meta_list[x-1][0] == meta_list[x][0] and meta_list[x-1][1] == meta_list[x][1] and math.fabs(meta_list[x-1][2]-meta_list[x][2]) < 3:
            new_meta_list.append(meta_list[x][:])
            new_meta_list[-1][2] = (meta_list[x-1][2] + meta_list[x][2])/2
            new_meta_list[-1][3] = meta_list[x-1][3] + meta_list[x][3]
            combined = True            
        else:
            if not combined:
                new_meta_list.append(meta_list[x-1])
            combined = False
        #print "new x:",x,new_meta_list
            
    if not combined:
        new_meta_list.append(meta_list[-1])
        
    #print "Neighbours Combined!", new_meta_list
    return new_meta_list


def test_cases_generator():
    test_cases = []
    test_case_id = 1
    
    st1 = SearchTerm()
    st1.word = 'abby'
    st1.occurrences = json.dumps([[3, 12, 101], [3, 12, 171], [3, 12, 175]])
    st2 = SearchTerm()
    st2.word = 'martha'
    st2.occurrences = json.dumps([[3, 12, 111], [3, 12, 171], [3, 12, 175], [3, 20, 150], [4, 24, 143]])
    res = [[3, 12, 101, 5], [3, 12, 111, 5], [3, 12, 171, 15], [3, 12, 175, 15], [3, 20, 150, 5], [4, 24, 143, 5]]
    t = TestCase(test_case_id, [st1,st2], res)
    test_case_id += 1
    test_cases.append(t)

    st1 = SearchTerm()
    st1.word = 'abc'
    st1.occurrences = json.dumps([[3, 12, 101], [3, 12, 175]])
    st2 = SearchTerm()
    st2.word = 'acd'
    st2.occurrences = json.dumps([[3, 12, 111], [3, 12, 175]])
    res = [[3, 12, 101, 5], [3, 12, 111, 5], [3, 12, 175, 15]]
    t = TestCase(test_case_id, [st1,st2], res)
    test_case_id += 1
    test_cases.append(t)
    
    st1 = SearchTerm()
    st1.word = 'aaa'
    st1.occurrences = json.dumps([[3, 12, 110], [3, 12, 175]])
    st2 = SearchTerm()
    st2.word = 'bbb'
    st2.occurrences = json.dumps([[3, 12, 111], [3, 12, 175]])
    res = [[3, 12, 110, 10], [3, 12, 175, 15]]
    t = TestCase(test_case_id, [st1,st2], res)
    test_case_id += 1
    test_cases.append(t)

    st1 = SearchTerm()
    st1.word = 'aaa'
    st1.occurrences = json.dumps([[3, 12, 110], [3, 12, 175]])
    st2 = SearchTerm()
    st2.word = 'bbb'
    st2.occurrences = json.dumps([[3, 12, 111], [3, 12, 175]])
    st3 = SearchTerm()
    st3.word = 'ccc'
    st3.occurrences = json.dumps([[3, 12, 112], [3, 12, 175]])
    res = [[3, 12, 110, 10], [3, 12, 111, 10], [3, 12, 175, 25]]
    t = TestCase(test_case_id, [st1,st2,st3], res)
    test_case_id += 1
    test_cases.append(t)

    st1 = SearchTerm()
    st1.word = 'aaa'
    st1.occurrences = json.dumps([[3, 12, 110], [3, 12, 175]])
    st2 = SearchTerm()
    st2.word = 'bbb'
    st2.occurrences = json.dumps([[3, 12, 114], [3, 12, 175]])
    st3 = SearchTerm()
    st3.word = 'ccc'
    st3.occurrences = json.dumps([[3, 12, 112], [3, 12, 175]])
    res = [[3, 12, 111, 10], [3, 12, 113, 10], [3, 12, 175, 25]]
    t = TestCase(test_case_id, [st1,st2,st3], res)
    test_case_id += 1
    test_cases.append(t)

    st1 = SearchTerm()
    st1.word = 'aaa'
    st1.occurrences = json.dumps([[3, 12, 110], [3, 12, 175]])
    st2 = SearchTerm()
    st2.word = 'bbb'
    st2.occurrences = json.dumps([[3, 12, 115], [3, 12, 175]])
    st3 = SearchTerm()
    st3.word = 'ccc'
    st3.occurrences = json.dumps([[3, 12, 113], [3, 12, 175]])
    res = [[3, 12, 110, 5], [3, 12, 114, 10], [3, 12, 175, 25]]
    t = TestCase(test_case_id, [st1,st2,st3], res)
    test_case_id += 1
    test_cases.append(t)

    st1 = SearchTerm()
    st1.word = 'aaa'
    st1.occurrences = json.dumps([[3, 12, 110], [3, 12, 175]])
    st2 = SearchTerm()
    st2.word = 'bbb'
    st2.occurrences = json.dumps([[3, 12, 110], [3, 12, 175]])
    st3 = SearchTerm()
    st3.word = 'ccc'
    st3.occurrences = json.dumps([[3, 12, 110], [3, 12, 113], [3, 12, 175]])
    st4 = SearchTerm()
    st4.word = 'ddd'
    st4.occurrences = json.dumps([[3, 12, 113], [3, 12, 175]])
    res = [[3, 12, 110, 25], [3, 12, 113, 15], [3, 12, 175, 35]]
    t = TestCase(test_case_id, [st1,st2,st3,st4], res)
    test_case_id += 1
    test_cases.append(t)
    
    st1 = SearchTerm()
    st1.word = 'aaa'
    st1.occurrences = json.dumps([[3, 12, 110], [4, 12, 175]])
    st2 = SearchTerm()
    st2.word = 'bbb'
    st2.occurrences = json.dumps([[3, 12, 111], [4, 12, 175]])
    st3 = SearchTerm()
    st3.word = 'ccc'
    st3.occurrences = json.dumps([[3, 12, 110], [3, 12, 113], [4, 12, 175]])
    st4 = SearchTerm()
    st4.word = 'ddd'
    st4.occurrences = json.dumps([[3, 12, 112], [4, 12, 175]])
    res = [[3, 12, 110, 20], [3, 12, 111, 10], [3, 12, 112, 10], [4, 12, 175, 35]]
    t = TestCase(test_case_id, [st1,st2,st3,st4], res)
    test_case_id += 1
    test_cases.append(t)

    return test_cases

def main():
    test_cases = test_cases_generator()
    for test_case in test_cases:
        #print test_case.op
        #print test_case.ip
        try:
            actual_output = search_logic(test_case.ip)
            assert test_case.op == actual_output
            print "Test Case Passed ", test_case.id
        except:
            print "Test Case Failed ", test_case.id
            print "Expected Output:", test_case.op
            print "Actual Output:", actual_output
    res = [[3, 12, 110, 20], [3, 12, 111, 10], [3, 12, 112, 10], [4, 12, 175, 35]]
    res.sort(key=lambda occurrence: occurrence[3], reverse=True)
    print res


if __name__ == '__main__':
    main()