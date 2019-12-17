import sys
import re

class KnowledgeBase():
    def __init__(self, KB):
        # covert sentence in KB to be CNF
        self.map = dict() # predicate => list(set, set, set)
        for clause in KB:
            if "=>" in clause:
                temp = clause.split("=>")
                beforeImplies = temp[0]
                totalList = set()
                afterImplies = temp[1].strip() # b len must be 1
                if(len(beforeImplies) == 1): # not a or b
                    temp0 = ""
                    if beforeImplies.strip()[0] == "~":
                        temp0 += beforeImplies.strip()[1:]
                    else:
                        temp0 = "~"
                        temp0 += beforeImplies.strip()
                    totalList.add(temp0)
                else:
                    temp1 = beforeImplies.split("&")
                    for single in temp1:
                        single = single.strip()
                        temp0 = ""
                        if single[0] == "~":
                            temp0 += single[1:]
                        else:
                            temp0 = "~"
                            temp0 += single
                        totalList.add(temp0)
                totalList.add(afterImplies)
                predicatesInList = self.getPredicates(totalList)
                for predicate in predicatesInList:
                    if predicate not in self.map:
                        temp = list()
                        temp.append(totalList)
                        self.map[predicate] = temp
                    else:
                        if totalList not in self.map[predicate]:
                            self.map[predicate].append(totalList)
            else:
                singleList = set()
                singleList.add(clause.strip())
                predicatesInList = self.getPredicates(singleList)
                for predicate in predicatesInList:
                    if predicate not in self.map:
                        temp = list()
                        temp.append(singleList)
                        self.map[predicate] = temp
                    else:
                        if singleList not in self.map[predicate]:
                            self.map[predicate].append(singleList)

    def getPredicates(self, sentences):
        # return a list of predicates
        res = list()
        for sentence in sentences:
            predicate = ""
            i = 0
            while sentence[i] != "(":
                predicate += sentence[i]
                i += 1
            res.append(predicate)
        return res

    def getPredicate(self, sentence):
        # return predicate from string
        res = ""
        i = 0
        while sentence[i] != "(":
            res += sentence[i]
            i += 1
        return res

    def getKB(self):
        return self.map

    def tell(self, query):
        tempMap = dict()
        newQuery = ""
        if query[0] == "~":
            newQuery = query[1:]
        else:
            newQuery = "~"
            newQuery += query
        predicate = self.getPredicate(newQuery)
        
        if predicate in tempMap:
            if query not in tempMap[predicate]:
                tempMap[predicate].append(query)
        else:
            tempMap[predicate] = []
            tempMap[predicate].append(query)
        
        resQueryList = [newQuery]
        return resQueryList, self.map


    def unification(self, x, y, z):
        # https://stackoverflow.com/questions/49101342/implementing-the-prolog-unification-algorithm-in-python-backtracking
        # Based on this solution
        if z == None:
            return None
        elif x == y:
            return z
        
        elif x[0] >= 'a' and x[0] <='z' and isinstance(x, str):
            #unify_var(x, y, sub)
            x = x.strip()
            if x in z:
                return self.unification(z[x], y, z)
            else:
                z[x] = y
                return z
        elif y[0] >= 'a' and y[0] <= 'z' and isinstance(y, str):
            y = y.strip()
            if y in z:
                return self.unification(z[y], x, z)
            else:
                z[y] = x
                return z
        
        elif isinstance(x, str) and isinstance(y, str) and "(" in x and "(" in y:
            start = 0
            end = 0
            x = x.strip()
            y = y.strip()
            for i in range(len(x)):
                if x[i] == "(":
                    start = i+1
                    break
            for i in range(len(x)):
                if x[i] == ")":
                    end = i
                    break
            variableX = x[start:end]
            tempX = variableX.split(",")
            for i in range(len(y)):
                if y[i] == "(":
                    start = i+1
                    break
            for i in range(len(y)):
                if y[i] == ")":
                    end = i
                    break
            variableY = y[start:end]
            tempY = variableY.split(",")
            #print(tempX, tempY)
            return self.unification(tempX, tempY, z)

        elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
            temp = self.unification(x[0], y[0], z)
            if len(x) > 1 and len(y) > 1:
                return self.unification(x[1:], y[1:], temp)
            else:
                return temp
        else:
            return None


    def merge(self, candidate1, candidate2, union):
        #print(union)
        for literal1 in candidate1:
            
            predicate1 = self.getPredicate(literal1)
            negatePredicate1 = ""
            if predicate1[0] == "~":
                negatePredicate1 = predicate1[1:]
            else:
                negatePredicate1 = "~"
                negatePredicate1 += predicate1
            for literal2 in candidate2:
                
                predicate2 = self.getPredicate(literal2)
                if negatePredicate1 == predicate2:
                    
                    subSets = self.unification(literal1, literal2, {})
                    
                    if subSets != None:
                        merged = set()
                        #print(union)
                        union.remove(literal1)
                        union.remove(literal2)
                        
                        for item in union:
                            tempItem = item
                            tempPredicate = self.getPredicate(tempItem)
                            
                            start = 0
                            end = 0
                            for i in range(len(tempItem)):
                                if tempItem[i] == "(":
                                    start = i+1
                                    break
                            for i in range(len(tempItem)):
                                if tempItem[i] == ")":
                                    end = i
                                    break
                            variableX = tempItem[start:end]
                            tempX = variableX.split(",")
                            newTempX = [subSets[x] if x in subSets else x for x in tempX]
                            newItem = tempPredicate + "("
                            for que in newTempX:
                                newItem += que
                                newItem += ","
                            newItem = newItem[:-1]
                            newItem += ")"
                            #print(newItem)
                                #tempItem = re.sub(variable, subSets[variable], tempItem)
                            merged.add(newItem)
                        #print(candidate1, candidate2, union, subSets, merged)
                        return list(merged)
        return None
 

    def resolve(self, query):
        newQueries, curMap = self.tell(query)
        iteration = 0
        newMergedList = []
        newMergedList.append(newQueries)
        
        while True:
            for queries in newMergedList:
                #print(queries)
                for query in queries:
                    key1 = self.getPredicate(query)
                    iteration += 1
                    if iteration == 1000:
                        return False
                    negateKey1 = ""
                    if key1[0] == "~":
                        negateKey1 = key1[1:]
                    else:
                        negateKey1 = "~"
                        negateKey1 += key1
                    if negateKey1 in curMap:
                        list2 = curMap[negateKey1]
                        
                        candidate1 = queries
                        
                        for candidate2 in list2:
                            #print(candidate1, candidate2)
                            
                            merged = self.merge(set(candidate1), set(candidate2), set(candidate1).union(set(candidate2)))

                            #print(candidate1, candidate2, merged)
                            if merged == []:
                                #print(candidate1, candidate2)
                                return True
                            else:
                                if query in newMergedList:
                                    newMergedList.remove(query)
                                if merged is not None:
                                    newMergedList.append(merged)
                                    #print(newMergedList)
                #print(newMergedList)
            
        return False


                        

    def deBug(self):
        print(self.map)


def main():
    numQueries = 0
    numKBs = 0
    i = 0
    queries = list()
    KB = set()
    with open("input.txt", "r") as f:
        for line in f.readlines():
            i += 1
            line = line.strip()
            if i == 1:
                numQueries = int(line)
            elif i >= 2 and i <= 1+numQueries:
                queries.append(line)
            elif i == 2+numQueries:
                numKBs = int(line)
            elif i >= 3+numQueries and i < 3+numQueries+numKBs:
                KB.add(line)
    f.close()
    #print(KB)
    knowledgeBase = KnowledgeBase(KB)
    #knowledgeBase.deBug()
    #print(queries)
    results = list()
    for query in queries:
        
        knowledgeBase.tell(query)
        #knowledgeBase.deBug()
        res = knowledgeBase.resolve(query)
        print(res)
        results.append(res)
    
    with open("output.txt", "w") as f:
        for i in range(len(results)):
            if i < len(results)-1:
                if results[i]:
                    f.write("TRUE" + "\n")
                else:
                    f.write("FALSE" + "\n")
            else:
                if results[i]:
                    f.write("TRUE")
                else:
                    f.write("FALSE")
    f.close()
        
        

if __name__ == "__main__":
    main()
    
