from Facet import Facet
import utils

factories = []

# Intended to be used as annotation by plugins
def FacetFactory (factory):
	factories.append(factory)
	return factory