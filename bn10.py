import random
debug = False

class vertex:
    def __init__(self, label):
        self.edge = []
        self.label = label
        self.bnd = float('inf')
        self.explored = False
        self.next = None
        
    def addEdge(self, e):
        for i in self.edge:
            if i.vertex1.label == e.vertex1.label:
                if i.vertex2.label == e.vertex2.label:
                    return
            elif i.vertex1.label == e.vertex2.label:
                if i.vertex2.label == e.vertex1.label:
                    return
                
        self.edge.append(e)

class edge:
    def __init__(self, w, v1, v2):
        if v1.label < v2.label:
            self.vertex1 = v1
            self.vertex2 = v2
            self.weight = w
            self.explored = False
        else:
            self.vertex1 = v2
            self.vertex2 = v1
            self.weight = w
            self.explored = False

    def otherVertex(self, v):
        if v.label == self.vertex1.label:
            return self.vertex2
        else:
            return self.vertex1


def storePathInList(p, L2):
    if not p == None:
        L2.append(p.label)
        storePathInList(p.next, L2)

    
def printPathFromVertex(p):
    if not p == None:
        print "vertex {0} {1}".format(p.label, p.bnd)
        printPathFromVertex(p.next)


def printPathFromList(L2):
    for i in L2:
        print "vertex {0}".format(i)

        
def printGraph(vertexSet):
    print "BEGIN PRINTING GRAPH\n\n"

    for i in range(1,len(vertexSet)):

        v = vertexSet[i]
        print "vertex label is {0}, bnd {1}".format(v.label, v.bnd)
        print "len of v.edge is {0}".format(len(v.edge))

        for j in range(0, len(v.edge)):
            e = v.edge[j]
            print "    Edge: {0},{1} weight {2}".format(e.vertex1.label,e.vertex2.label, e.weight)

        print "done with vertex: ", v.label
        
    print "END PRINTING GRAPH\n\n"


class path:
    def __init__(self, v):
        self.v = v
        self.next = None


def setUnExplored(vertexSet):
    for i in range(1,len(vertexSet)):
        vertexSet[i].explored = False


def loadFile(vertexSet):
    f = open("b2.txt", "r")
    for line in f:
        s = line.strip()
         
        L = s.split('\t')
        sourceV = 0
        v = vertexSet[int(L[0])]
        if v == 0:
            sourceV = vertex(int(L[0]))
            vertexSet[int(L[0])] = sourceV
        else:
            sourceV = v

        for i in L[1:]:
            f = [float(x) for x in i.split(',')]
            sinkV = 0
            v = vertexSet[int(f[0])] 
            if v == 0:
                sinkV = vertex(int(f[0]))
                vertexSet[int(f[0])] = sinkV
            else:
                sinkV = v

            e = edge(f[1], sourceV, sinkV)
            
            sourceV.addEdge(e)
            sinkV.addEdge(e)


## remember update vertexCount, source and dest variables as necessary

vertexCount = 17
vertexSet = [0 for x in range(0,vertexCount)]
        
def run():
    loadFile(vertexSet)
    
    if debug:
        printGraph()

    dest = vertexSet[10]
    source  = vertexSet[13]
    findMinLoop(source, dest)


def findMinLoop(source, dest):
    """ See comment in findMin(). The function findMin is run initially once to find the bottleneck for source to dest. And after that we 
    reprocess any cycles we encountered in the very FIRST call to findMin(). 

    Running Time:  Each findMin takes O(E) where E = number of edges. For every cycle we find, we will do one more time. Assume k cycles. 
    Running Time = O(kE). If k is small compared to E, then O(kE) = O(E)
    """
    dest.bnd = 0
    source.explored = True
    redoList = []  ## we will store all vertices through which we have reached source (a cycle)

    findMin(source, source, dest, redoList)
    print "before redoList: Bottleneck of source {0} to dest {1} is {2}".format(source.label, dest.label, source.bnd)

    L2 = [0, []]
    L2[0] = source.bnd

    storePathInList(source, L2[1])
    printPathFromVertex(source)

    print "\n\n"
    for i in redoList:
        print "****** {0}, {1}".format(i[0].label, i[1].weight)

    for i in redoList:
        L = []
        setUnExplored(vertexSet)
        source.explored = True
        v = i[0]  ## explore bottleneck of v to dest 
        e = i[1]  ## e connects source to v
        y = L2[0] # previously smallest bottleneck
        
        findMin(v, source, dest, L) ## we don't care about L anymore
        
        x = max(e.weight, v.bnd)
        if x < y:          ## see if path from source via v is better than previously computed path
            L2[1][:] = []  ## clear the previous list
            L2[0] = x       ## set the new bottleneck of source
            storePathInList(source, L2[1])

    print "after redoList: bottleneck of source {0} to dest {1} is {2}".format(source.label, dest.label, source.bnd)
    printPathFromList(L2[1])    

            

def findMin(v, source, dest, redoList):
    """Algorithm:
    For each edge e with vertices (v,u) directly connected to v, 
        mark u explored
        run findMin again with vertex u. This will give us u.bnd
        Take the max of u.bnd and e.weight. This is bnd for vertex v to dest via u. Store (max, u) in a list
        Find the smallest max from this list. Update v.bnd if its existing bnd is greater than the newly found bnd. Also update v.next to point to u

        Invariant: At any point, smallest bottleneck(v) = max(u.bnd, e.weight) for all edges (v,u) adjacent to  v. For this invariant to  
        be true, two conditions need to hold. One path out of v cannot trace the other path at some point in the future. This is not possible as 
        a vertex which is seen first is marked as explored and so if we ever see this vertex again we would not move forward. 

        Secondly, as long is we move further away from source or in other words, we do not hit upon the source vertex, in a given path 
        from v to dest, we can be assured that bottleneck of e = max (e.weight, bottleneck of next vertex in path). It is easy to see that this 
        condition will fail if we encounter the source. 

        So if we ever reach the source via some directly connected vertex w, then any bottleneck calculated for w could be incorrect. 
        However, if a cycle to the source was found, then re-process the bottleneck for w. We do this by storing w in redoList and processing 
        again. The bulk of findMinLoop() is devoted to addressing this reprocessing of cycles. 
    """
            
    if v.label == dest.label:  # we have reached dest, so mark v.bnd to 0 
        v.bnd = 0
        v.explored = False
        v.next = None
        return

    ml = []
    for e in v.edge:   ## compute bottleneck of v via each of its directly connected edges and store in list ml
        u = e.otherVertex(v)
        
        if not u.label == source.label:  ## no cycle 
            
            if not u.explored:
                u.explored = True
                findMin(u, source, dest, redoList)
                
            n = max(u.bnd, e.weight)   ## n is the bottleneck of v to dest via u
            ml.append((n, u))                ## store both the bottleneck and the other vertex of this edge u
            x = min(ml)                            ## find the smallest of the bottleneck of v to dest via all of its edges
            
            if x[0] < v.bnd:   ## if newly found bnd is less than existing bnd, update v.bnd and v.next
                v.bnd = x[0]
                v.next = x[1]
                
        else:   ## u.label == source.label
            ## implies a cycle. If cycle exists, we need to process findMin from this vertex later
            ## for now, add tuple (v, e) to redoList as a tuple
            if not v.explored:
                redoList.append((v,e))

    return

