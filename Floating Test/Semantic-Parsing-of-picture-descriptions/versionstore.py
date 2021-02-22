def gen(self,s):
        """ Floating Parser"""
        words = s.split()
        maxlen = len(words)+3 
        chart = defaultdict(lambda:defaultdict(set))
        agenda = []
        # construct predicates according to utterance
        for word in words:
            for categorie,function in self.lexicon[word]:
                try:
                    semantic = self.functions[function]
                except:
                    semantic = eval(function)
                item = ParseItem(categorie,1,semantic,{(word,function)})
                chart[categorie,1].add(item)
                agenda.append(item)
        # TODO: construct predicates out of the air 
        for function in functions:
            pass
        # construct longer formulas using this components:
        maxlen_currently = 1
        while (maxlen_currently <= maxlen):
            item = agenda.pop(0)
            s1 = item.s
            c1 = item.c
            components1 = item.components
            semantic1 = item.semantic
            new_items = set()
            for c2,s2 in chart:
                s_new = 1+s1+s2
                if maxlen_currently < s_new:
                    maxlen_currently = s_new
                if (c2,c1) in self.rules:
                     c_new = self.rules[c2,c1]
                     for item2 in chart[c2,s2]:
                         #print(semantic1,item2.semantic,c1,item2.c)
                         semantic_new = item2.semantic (semantic1)
                         components_new = components1.union(item2.components)
                         item_new = ParseItem(c_new,s_new,semantic_new,components_new)
                         agenda.append(item_new)
                         new_items.add(item_new)
                if (c1,c2) in self.rules:
                     c_new = self.rules[c1,c2]
                     for item2 in chart[c2,s2]:
                         semantic_new = semantic1 (item2.semantic)
                         components_new = components1.union(item2.components)
                         item_new = ParseItem(c_new,s_new,semantic_new,components_new)
                         agenda.append(item_new)
                         new_items.add(item_new)
            for new_item in new_items:
                chart[new_item.c,new_item.s].add(new_item)
        results = []
        for (c,s) in chart:
            print(c,s)
            for item in chart[c,s]:
                print("\t",item.c,item.s,item.semantic,item.components)
            if c =='V':
                for item in chart[c,s]:
                    results.append(item)
        return results
