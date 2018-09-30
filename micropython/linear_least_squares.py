#!/usr/bin/python3

#Thanks to zmatt for this magic!

def dot(v, w):
    a = 0.
    for i in range( len(v) ):
        a += v[i] * w[i]
    return a

def vec_divs(v, a):
    for i in range( len(v) ):
        v[i] /= a

def vec_addsv(v, a, w):
    for i in range( len(v) ):
        v[i] += a * w[i]

def gaussian_elimination(M):
    n = len(M)

    for i in range(n):
        for j in range(i+1, n):
            if abs( M[j][i] ) > abs( M[i][i] ):
                M[i], M[j] = M[j], M[i]

        vec_divs( M[i], M[i][i] )

        for j in range(n):
            if j != i:
                vec_addsv( M[j], -M[j][i], M[i] )


# K= [ 0.010, 0.011, 0.012, 0.013 ]
# C = 1234
#
# measurements = [
#     [ C*.70/K[0], C*.10/K[1], C*.10/K[2], C*.10/K[3],  C ],
#     [ C*.10/K[0], C*.10/K[1], C*.70/K[2], C*.10/K[3],  C ],
#     [ C*.10/K[0], C*.70/K[1], C*.10/K[2], C*.10/K[3],  C ],
#     [ C*.10/K[0], C*.10/K[1], C*.10/K[2], C*.70/K[3],  C ],
#     [ C*.25/K[0], C*.25/K[1], C*.25/K[2], C*.25/K[3],  C ],
# ]
#
#
# M = [ [0] * 5 for i in range(4) ]
#
# for data in measurements:
#     for i in range(4):
#         vec_addsv( M[i], data[i], data )
#
# gaussian_elimination( M )
#
# K = [ M[i][4] for i in range(4) ]
# print( K )
#
# # calculate mean square error
# mse = 0.
# for data in measurements:
#     weight = dot( K, data )
#     err = weight - data[4]
#     mse += err * err
# mse /= len( measurements )
# print( mse )
