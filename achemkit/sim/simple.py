"""
This contains a number of simple simulation classes, based on subclasses of
:py:class:`achemkit.Reactor`.

Also contains some convenience functions for these reactors.
"""

import random
import itertools
try:
    import cPickle as pickle
except ImportError:
    import pickle as pickle


import umpf
    
from achemkit.utils.utils import get_sample
from achemkit import OrderedFrozenBag
from achemkit import Reactor
from achemkit import Event
from achemkit import Bucket

class ReactorEnumerate(Reactor):
    """
    Reactor object designed to exaustively enumerate all possible reactant 
    collections, adding new reactant collections as novel products appear.
    """
    def __init__(self, achem, mols):
        """
        :param achem: :py:class:`achemkit.achem.AChem` object or equivalent.
        :param mols: Initial molecular species.
        """
        super(ReactorEnumerate, self).__init__(achem, mols)
        self.maxmols = len(mols)
        self.mols = []
        self.tested = []
        self.untested = []
                
        for mol in mols:
            self.add_mol(mol)
            
    def add_mol(self, mol):
        """
        Internal utility function used to ensure molecular species have the
        relevant reaction combinations added.
        
        :param mol: Molecular species to add to reactor.
        """
        if mol not in self.mols:
            self.mols.append(mol)
            noreactants = self.achem.noreactants
            try:
                noreactants = set(noreactants)
            except TypeError:
                #not an itterable, single number
                noreactants = set([noreactants])
            for i in noreactants:
                for others in itertools.combinations(self.mols, i-1):
                    reactants = (mol,)+others
                    reactants = OrderedFrozenBag(reactants)
                    assert reactants not in self.tested
                    self.untested.append(reactants)
        
    def do(self, count):
        """
        Enumerate all possible reactant collections and determine products
        via :py:meth:`achemkit.achem.AChem.all_reactions`.
        
        Uses :py:mod:`umpf` for parallelism.
        
        :param integer count: Maximum number of additional molecular species to 
                              discover.
        :rtype: yields :py:class:`achemkit.Event` objects.
        """
        self.maxmols += count
        while len(self.mols) < self.maxmols and len(self.untested) > 0:
            untested = tuple(self.untested)
            self.untested = []
            results = umpf.map(self.achem.all_reactions, untested)
            while len(self.mols) < self.maxmols:
                try:
                    reactions = results.next()
                except StopIteration:
                    break
                else:
                    for reaction in reactions:
                        reactants, products = reaction
                        e = Event(0.0, reactants, products, reactions[reaction])
                        yield e
                        for product in products:
                            self.add_mol(product)

class ReactorItterative(Reactor):
    """
    Reactor object that proceeds one reaction at a time.
    """
    def __init__(self, achem, mols, rngseed=None):
        """
        :param achem: :py:class:`achemkit.achem.AChem` object or equivalent.
        :param mols: Molecules to start from.
        :param rngseed: Instance of :py:class:`random.Random` or seed for 
                        :py:class:`random.Random`
        """
        super(ReactorItterative, self).__init__(achem, mols)
        self.maxtime = 0.0
        self.time = 1.0
        if isinstance(rngseed, random.Random):
            self.rng = rngseed
        else:
            self.rng = random.Random(rngseed)
        
        
    def do(self, time):
        """
        Repeatedly determine a random collection of reactants and replace them 
        with the products generated by :py:meth:`achemkit.achem.AChem.react`.
                
        Uses :py:mod:`umpf` for parallelism.
        
        :param float time: Time to simulate, at a rate of one reaction per unit.
        :rtype: yields :py:class:`achemkit.Event` objects.
        """
        self.maxtime += time
        while self.time < self.maxtime:
            self.mols = tuple(self.rng.sample(self.mols, len(self.mols)))
            
            noreactants = 2
            reactants = OrderedFrozenBag(self.mols[:noreactants])
            self.mols = self.mols[noreactants:]
            
            products = self.achem.react(reactants)
            self.mols += tuple(products)
            
            e = Event(self.time, reactants, products)
            yield e
            self.time += 1.0
            
                
class ReactorStepwise(Reactor):
    """
    Reactor object that reacts all molecules in parallel.
    """
    def __init__(self, achem, mols, rngseed=None):
        """
        :param achem: :py:class:`achemkit.achem.AChem` object or equivalent.
        :param mols: Molecules to start from.
        :param rngseed: Instance of :py:class:`random.Random` or seed for 
                        :py:class:`random.Random`
        """
        super(ReactorStepwise, self).__init__(achem, mols)
        self.maxtime = 0.0
        self.time = 0.0
        if isinstance(rngseed, random.Random):
            self.rng = rngseed
        else:
            self.rng = random.Random(rngseed)
        
        
    def do(self, time):
        """
        Assign all molecules to a collection of reactants. Use the combined
        collections of products as the new molecules.
                
        Uses :py:mod:`umpf` for parallelism.
        
        :param float time: Time to simulate, at a rate of one step per unit.
        :rtype: yields :py:class:`achemkit.Event` objects.
        """
        self.maxtime += time
        while self.time < self.maxtime:
            self.mols = tuple(self.rng.sample(self.mols, len(self.mols)))
            newmols = ()
            allreactants = []
            while len(self.mols) > 0:
                noreactants = get_sample(self.achem.noreactants)
                if noreactants <= len(self.mols):
                    reactants = self.mols[:noreactants]
                    self.mols = self.mols[noreactants:]                
                    allreactants.append(OrderedFrozenBag(reactants))
                else:
                    break
                    
            allproducts = umpf.map(self.achem.react, allreactants)
            results = itertools.izip(allreactants, allproducts)
            for reactants, products in results:
                e = Event(self.time, reactants, products)
                newmols += tuple(products)
                yield e
                
            self.mols = newmols
            self.time += 1.0
            
def sim_enumerate(achem, mols, maxmols):
    """
    Wrapper for :py:class:`ReactorEnumerate`
    to return :py:class:`Event` objects.
    """
    sim = ReactorEnumerate(achem, mols)
    for e in sim.do(maxmols):
        yield e
        
def sim_itterative(achem, mols, maxtime, rng = None):
    """
    Wrapper for :py:class:`ReactorItterative`
    to return :py:class:`Event` objects.
    """
    sim = ReactorItterative(achem, mols, rng)
    for e in sim.do(maxtime):
        yield e
    

def sim_stepwise(achem, mols, maxtime, rng=None):
    """
    Wrapper for :py:class:`ReactorStepwise`
    to return :py:class:`Event` objects.
    """
    sim = ReactorStepwise(achem, mols, rng)
    for e in sim.do(maxtime):
        yield e

def net_enumerate(achem, mols, maxmols, rng=None):
    """
    Wrapper for :py:func:`sim_enumerate`
    to return a :py:class:`ReactionNetwork` object.
    """
    events = sim_enumerate(achem, mols, maxmols)
    bucket = Bucket(events)
    net = bucket.reactionnet
    return net
