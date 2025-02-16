import numpy as np
from ansys.mapdl.core import launch_mapdl

nelx = 10
nely = 10
nelz = 10
rho = 0.5
theta = 0.1
phi = 0

#Initialisation 
D = {}
D['nnode'] = (nelx + 1) * (nely + 1) * (nelz + 1)  # number of nodes in model
D['nel'] = nelx * nely * nelz  # number of elements in model
D['etype'] = 3  # element type (only one per model)
D['nelx'] = nelx
D['nely'] = nely
D['nelz'] = nelz
D['elname'] = 'elemental_3D'
D['ndof'] = 3
D['nenode'] = 8

nnode = (nelx + 1) * (nely + 1) * (nelz + 1)  # number of nodes in model
nel= nelx * nely * nelz  # number of elements in model
etype = 3  # element type (only one per model)
ndof = 3 # nombre de degré de liberté pour chaque noeud
nenode = 8 # nombre de noeuds pour chaque element

# Génération du maillage
xloc1, yloc1, zloc1 = np.meshgrid(np.arange(nelx + 1),np.arange(nely, -1, -1),np.arange(nelz + 1),indexing='ij')

# 🔹 Lancer MAPDL
mapdl = launch_mapdl()

# 🔹 Entrer dans le mode PREP7 (préprocesseur)
mapdl.prep7()

# 🔹 Création d'un bloc 3D
mapdl.block(0, nelx, 0, nely, 0, nelz)

# 🔹 Définition des propriétés du matériau
E = 210e9  # Module de Young (Pa) (Acier)
nu = 0.3   # Coefficient de Poisson
mapdl.mp("EX", 1, E)
mapdl.mp("PRXY", 1, nu)

# 🔹 Définition du maillage
mapdl.et(1, "SOLID185")  # Type d'élément 3D (modifiez selon vos besoins)
mapdl.esize(1)   # Taille élémentaire pour homogénéité
mapdl.vmesh('ALL')  # Maillage du volume

# 🔹 Sélection des nœuds de la face X = 0 (plan YZ)
mapdl.nsel("S", "LOC", "X", 0)

# 🔹 Appliquer un encastrement (tous les degrés de liberté fixés)
mapdl.d("ALL", "UX", 0)
mapdl.d("ALL", "UY", 0)
mapdl.d("ALL", "UZ", 0)

# 🔹 Sélection des nœuds de l'arête supérieure (X = lx, Y = ly, Z = lz)
mapdl.nsel("S", "LOC", "X", nelx)
mapdl.nsel("R", "LOC", "Z", nelz)  # Réduction à Z = lz

# 🔹 Application de la force en Z sur ces nœuds
force_value = -1e6  # Force descendante (N)
mapdl.f("ALL", "FZ", force_value)
mapdl.finish()

# 🔹 Passer en mode solution (SOLU)
mapdl.slashsolu()  # Mode solution
mapdl.solve()      # Exécuter l'analyse statique

# 🔹 Mode post-traitement
mapdl.post1()
mapdl.set(1)  # Lire la première solution

# 🔹 Récupérer les déplacements nodaux
mapdl.allsel()
ux = mapdl.post_processing.nodal_displacement("X")
uy = mapdl.post_processing.nodal_displacement("Y")
uz = mapdl.post_processing.nodal_displacement("Z")
ux = np.array(ux)
uy = np.array(uy)
uz = np.array(uz)
utot = np.column_stack((ux, uy, uz))

connectivity = mapdl.mesh.elem
cleaned_connectivity = [[int(node) for node in elem] for elem in connectivity]
ielem = [elem[-8:] for elem in cleaned_connectivity]

# 🔹 Affichage du maillage et des conditions de support
mapdl.eplot(show_node_numbering=True, show_element_numbering=True)

# 🔹 Fermeture de MAPDL (désactiver si vous voulez faire d'autres analyses)
mapdl.exit()