# -*- coding: utf-8 -*-
"""Untitled26.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kz6f_ieEzITyvESVLcBapfzapxMQzdLK
"""

#  Program Algoritma Simulated Annealing
#  Refererensi Won Y. Yang dkk
#  Dibuat Oleh Asrin (2022)
#  KDimodifikasi oleh Annisa Adelwa Zsada (2024)


import time
import numpy as np
import numpy.matlib
import pandas as pd
import matplotlib.pyplot as plt

''' Input parameter '''
start_time = time.time()
# Calling the input model parameters
itin = pd.read_excel('/content/Square_ModelHori.xlsx', sheet_name='Sheet1')  # data call
tin = itin.head()
# Calling the Gravity Anomaly
grav = np.genfromtxt('/content/datsinhorizontal.dat')  # data g obs
f = np.array(grav[:, 1])
xxx = np.array(grav[:, 0])

# untuk memanggil data dari parameter model pada excel
# Parameter Model Blok 2-D
nlay = int(itin.loc[0, 'nb'])  # Banyak grid
nxg = int(itin.loc[0, 'nx'])  # Banyak cell lateral
nzg = int(itin.loc[0, 'nz'])  # Banyak cell vetikal
dx = int(itin.loc[0, 'dx'])  # Dimensi cell lateral (m), spasi stasiun
dh = int(itin.loc[0, 'dz'])  # Dimensi cell vetikal (m),  dept (kedalaman)
model = np.array([nxg, nzg, dx, dh])

l = itin.loc[1, :]  # lower earch of parameter
l = np.array([l[0:int(nlay)]])
u = itin.loc[2, :]  # upper search of parameter
u = np.array([u[0:int(nlay)]])

x0 = l + (u - l) / 2  # initial guess
kmax = 1000  # Jumlah Iterasi
q = 1
TolFun = 1e-8 #parameter yang menentukan kriteria konvergensi atau tingkat toleransi kesalahan yang diperbolehkan dalam pencarian solusi


def forward_grav(rho, model):  # mendefinisikan forward modeling
    # parameter modelnya
    G = 6.6732e-11  # Kontanta Gravirtasi damalm Mks
    dx = model[3]  # (m)
    dh = model[2]  # (m)
    nx = model[0]
    nz = model[1]
    d = dx  # station spacing
    h = dh  # depth spacing (thickness)

    V = rho
    V = np.reshape(rho, (nz, nx))  # reshape (untuk mengubah bentuk array tanpa mengubah datanya.)
    VV = V.transpose().ravel()  # ravel (mengembalikan referensi ke data asli, dan tidak menghasilkan data salinan dan lbih efisien)

    x1 = np.arange(0, (nx - 1) * dx + dx, dx)
    x = x1 + d / 2
    z1 = np.transpose([np.arange(0, ((nz + 1) * h - 10), h)])
    z = z1 + h / 2
    nb = nx * nz

    xx = np.array(numpy.matlib.repmat(x, nz, 1))
    xx = xx.transpose().ravel()
    zz = np.array(numpy.matlib.repmat(z, 1, nx))
    zz = zz.transpose().ravel()

    AA = np.zeros((nx, nb))  # parameter model yang digunakan nb, nx

    for i in range(nx):
        for j in range(nb):
            r1 = ((zz[j] - h / 2) ** 2 + (x[i] - xx[j] + d / 2) ** 2) ** 0.5
            r2 = ((zz[j] + h / 2) ** 2 + (x[i] - xx[j] + d / 2) ** 2) ** 0.5
            r3 = ((zz[j] - h / 2) ** 2 + (x[i] - xx[j] - d / 2) ** 2) ** 0.5
            r4 = ((zz[j] + h / 2) ** 2 + (x[i] - xx[j] - d / 2) ** 2) ** 0.5
            theta1 = np.arctan((x[i] - xx[j] + d / 2) / (zz[j] - h / 2))
            theta2 = np.arctan((x[i] - xx[j] + d / 2) / (zz[j] + h / 2))
            theta3 = np.arctan((x[i] - xx[j] - d / 2) / (zz[j] - h / 2))
            theta4 = np.arctan((x[i] - xx[j] - d / 2) / (zz[j] + h / 2))
            AA[i, j] = 2 * G * ((x[i] - xx[j] + d / 2) * np.log((r2 * r3) / (r1 * r4))
                                + d * np.log(r4 / r3) - (zz[j] + h / 2) * (theta4 - theta2)
                                + (zz[j] - h / 2) * (theta3 - theta1))

    gm = np.dot(AA, VV) * 1e5
    return gm  # mendapatkan nilai Forwad nya


x = x0
fx = f
xo = x
fo = fx

# xx=list()
# ff=list()
# dff=list()

xx = []
ff = []
dff = []
TT = []
# stopping Criteria
for k in range(kmax):  # pembuatan iterasi sebanyak nilai Kmax (100 kali)
    Ti = 1000 * ((0.99) ** k)  # update temperatur
    mu = 10 ** (100 * ((k / kmax) ** q)) #update pertubasi parameter
    # print(mu)
    # fungsi mu_inv
    def mu_inv(y, mu):
        x = np.sign(y) * (1.0 / mu) * ((1.0 + mu) ** abs(y) - 1.0)
        return x

    dx = mu_inv(2 * np.random.rand(np.size(x)) - 1, mu) * (u - l)
    x1 = x + dx
    x1 = (x1 < l) * l + (l <= x1) * (x1 <= u) * x1 + (u < x1) * u

    # fungsi forward (untuk memanggil nilai forwardnya, untuk di inversikan)
    gm = forward_grav(x1, model)
    fx1 = gm  #hasil forward (gobs)
    Nf = len(fx1)
    df = np.sqrt ( 1/Nf * (np.sum((fx1 - fx) ** 2)))

    if np.any(df) < 0 or np.random.rand() < np.any(np.exp(Ti * df / (abs(fx) + np.spacing(fx)) / TolFun)):
        x = x1
        fx = fx
    if np.any(fx) < np.any(fo):
        xo = x
        fo = fx1
    fx11 = np.transpose(fx1)
    f11 = np.transpose(f)
    dfo = np.sqrt (1 / Nf * (np.sum((fx11 - f11) ** 2))) #dimodif

#dimodif
    p = 0.9
    iteration = {}
    iteration[p] = p
    if iteration[p] > kmax:
        break



    TT.append(Ti)
    dff.append(dfo)
    xx.append(x1)
    # ff = fx1
    ff.append(fx1)
    # print(e_min)
    # print(ff)

#ditambahkan
    print("Iteration:", k)
    print("Temperature:", Ti)
    print("Misfit:", dfo)
    print("-" * 50)

# Searching the global solution
# dff = np.reshape(dff,(1,1000))
# xx = np.reshape(xx,(36000,1))
ff = np.reshape(ff, (kmax, nxg))  # pencarian solusi global,

e_min = np.array([min(dff)])

# print(xx.shape)
# print(ff.shape)

ff_min = np.where(dff == e_min)
ff_sol = ff[ff_min, :].ravel()
xsol = np.reshape(np.transpose([xx]), (nlay, kmax))
xx_sol = xsol[:, ff_min]

# xx_sol=np.array([xx_sol[:,1,0]])
VV2 = xx_sol.ravel().transpose()
VV = np.reshape(xx_sol, (nzg, nxg))

zSA1 = np.arange(0, (nzg - 1) * dh, dh)
zSA = zSA1 + 10 / 2

# Mengubah extent agar dimulai dari 1
extent_x_min = 0
extent_x_max = xxx.max() + 5
extent_z_min = 0
extent_z_max = zSA.max() + 15

plt.figure('Gambar 1', figsize=(9, 7.5))
plt.subplot(2, 1, 1).set(xlim=(0, 90), ylim=(0, 0.60))
plt.plot(xxx, f, 'ob-', label='G-obs')
plt.plot(xxx, ff_sol, 'or-', label='Inversi SA')
plt.legend()
plt.title('Penampang Hasil Inversi SA 2D Gravitasi')
plt.xlabel('Spasi [M]')
plt.ylabel('Anomali Medan Gravitasi [mGal]')
plt.subplot(2, 1, 2)
a = plt.imshow(VV, extent=(extent_x_min, extent_x_max, extent_z_max, extent_z_min),
               aspect='auto', cmap='viridis')
plt.ylabel('Kedalaman [M]')
plt.colorbar(a, orientation='horizontal')
plt.clim(100, 2000)
plt.grid(which='major')

plt.figure('Gambar 2', figsize=(9, 7.5))
plt.subplot(2, 1, 1)
plt.plot(TT, '-b', label='Temperature')
plt.title('Kurva Penurunan Temperatur Dan Misfit ')
plt.xlabel('Iterasi')
plt.ylabel('Temperature')
plt.legend()
plt.subplot(2, 1, 2)
plt.plot(dff, '-r', label='Misfit')
plt.xlabel('Iterasi')
plt.ylabel('Misfit [mGal]')
plt.legend()
# plt.plot(np.arange(0,kmax),ff,'.r')
print(VV)
print('=' * 10 + 'batas' + '=' * 10)
print(e_min)
print("--- %s seconds ---" % (time.time() - start_time))
plt.show()

print(xxx, f)
print(xxx, ff)

#ditambahkan
# Mencari iterasi dengan misfit terkecil
iterasi_min = np.argmin(dff)
print("Iterasi dengan Misfit Terkecil:", iterasi_min)
print("Hasil Data Inversi pada Iterasi Terkecil:")
print("Spasi [M] - Anomali Medan Gravitasi [mGal]")
for i in range(len(xxx)):
    print("{:.2f} - {:.4f}".format(xxx[i], ff[iterasi_min, i]))


# Menampilkan parameter model dari inversi
print("Parameter Model dari Inversi:")
print(f"Jumlah grid vertikal (nz): {nzg}")
print(f"Jumlah grid horizontal (nx): {nxg}")
print(f"Jumlah blok (nb): {nlay}")
print(f"Dimensi grid horizontal (dx): {dx}")
print(f"Dimensi grid vertikal (dz): {dh}")