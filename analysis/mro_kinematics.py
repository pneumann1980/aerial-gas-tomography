import numpy as np

def getRotationMatrixX(a, degrees=False):
    if degrees: a = np.deg2rad(a)
    
    sa = np.sin(a)
    ca = np.cos(a)
    
    return np.array([[1,   0,  0],
                     [0,  ca, sa],
                     [0, -sa, ca]])

def getRotationMatrixY(a, degrees=False):
    if degrees: a = np.deg2rad(a)
    
    sa = np.sin(a)
    ca = np.cos(a)
    
    return np.array([[ca, 0, -sa],
                     [0,  1,   0],
                     [sa, 0,  ca]])

def getRotationMatrixZ(a, degrees=False):
    if degrees: a = np.deg2rad(a)
    
    sa = np.sin(a)
    ca = np.cos(a)
    
    return np.array([[ ca, sa, 0],
                     [-sa, ca, 0],
                     [  0,  0, 1]])

def toQuaternionFromRotationMatrix(m):
    if m[2,2] < 0:
        if m[0,0] > m[1,1]:
            t = 1 + m[0,0] - m[1,1] - m[2,2]
            q = np.array([t, m[0,1]+m[1,0], m[2,0]+m[0,2], m[1,2]-m[2,1]])
        else:
            t = 1 - m[0,0] + m[1,1] - m[2,2]
            q = np.array([m[0,1]+m[1,0], t, m[1,2]+m[2,1], m[2,0]-m[0,2]])
    else:
        if m[0,0] < -m[1,1]:
            t = 1 - m[0,0] - m[1,1] + m[2,2]
            q = np.array([m[2,0]+m[0,2], m[1,2]+m[2,1], t, m[0,1]-m[1,0]])
        else:
            t = 1 + m[0,0] + m[1,1] + m[2,2]
            q = np.array([m[1,2]-m[2,1], m[2,0]-m[0,2], m[0,1]-m[1,0], t])
    
    return q * (0.5 / np.sqrt(t))

def getCrossProductMatrix(v):
    return np.array([[    0, -v[2],  v[1]],
                     [ v[2],     0, -v[0]],
                     [-v[1],  v[0],  0]])

def getRotationMatrixFrom2Vectors(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    
    v = np.cross(a, b)
    #s = np.linalg.norm(v) # sin
    c = np.dot(a, b) # cos
    
    v_cross = getCrossProductMatrix(v)
    
    return np.identity(3) + v_cross + np.dot(v_cross, v_cross)/(1.0 + c)

if __name__ == '__main__':
    r1 = getRotationMatrixX(90, degrees=True)
    r2 = getRotationMatrixX(-90, degrees=True)
    v1 = np.array([0,1,0])
    print(r1@v1)
