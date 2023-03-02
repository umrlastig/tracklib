"""Class to manage cinematic computations on GPS tracks"""

import math
import progressbar
import numpy as np

import tracklib.core.Utils as utils
import tracklib.algo.Stochastics as Stochastics

MODE_OBS_AS_SCALAR = 0
MODE_OBS_AS_2D_POSITIONS = 1
MODE_OBS_AS_3D_POSITIONS = 2
MODE_OBS_AND_STATES_AS_2D_POSITIONS = 3
MODE_OBS_AND_STATES_AS_3D_POSITIONS = 4
MODE_STATES_AS_2D_POSITIONS = 5
MODE_STATES_AS_3D_POSITIONS = 6

MODE_VERBOSE_NONE = 0
MODE_VERBOSE_ALL = 1
MODE_VERBOSE_PROGRESS = 2
MODE_VERBOSE_PROGRESS_BY_EPOCH = 3


def DYN_MAT_2D_CST_POS():
    """TODO"""
    return np.array([[1, 0], [0, 1]])


def DYN_MAT_3D_CST_POS():
    """TODO"""
    return np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])


def DYN_MAT_2D_CST_SPEED(dt):
    """TODO"""
    return np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]])


def DYN_MAT_2D_CST_ACC(dt):
    """TODO"""
    dt2 = 0.5 * dt ** 2
    return np.array(
        [
            [1.0, 0.0, dt, 0.0, dt2, 0.0],
            [0.0, 1.0, 0.0, dt, 0.0, dt2],
            [0.0, 0.0, 1.0, 0.0, dt, 0.0],
            [0.0, 0.0, 0.0, 1.0, 0.0, dt],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        ]
    )


def DYN_MAT_3D_CST_SPEED(dt):
    """TODO"""
    return np.array(
        [
            [1, 0, 0, dt, 0, 0],
            [1, 0, 0, 0, dt, 0],
            [1, 0, 0, 0, 0, dt],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ]
    )


def DYN_MAT_3D_CST_ACC(dt):
    """TODO"""
    dt2 = 0.5 * dt ** 2
    return np.array(
        [
            [1.0, 0.0, 0.0, dt, 0.0, 0.0, dt2, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0, dt, 0.0, 0.0, dt2, 0.0],
            [0.0, 0.0, 1.0, 0.0, 0.0, dt, 0.0, 0.0, dt2],
            [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, dt, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, dt, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, dt],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        ]
    )


def DYN_MAT_2D_CST_SPEED_COV(dt, std_acc):
    """TODO"""
    G = np.array([[0.5 * dt ** 2], [0.5 * dt ** 2], [dt], [dt]])
    return std_acc ** 2 * G @ G.transpose()


def DYN_MAT_3D_CST_SPEED_COV(dt, std_acc):
    """TODO"""
    G = np.array([[0.5 * dt ** 2], [0.5 * dt ** 2], [0.5 * dt ** 2], [dt], [dt], [dt]])
    return std_acc ** 2 * G @ G.transpose()


def DYN_MAT_2D_CST_ACC_COV(dt, std_jrk):
    """TODO"""
    G = np.array(
        [
            [1.0 / 6.0 * dt ** 3],
            [1.0 / 6.0 * dt ** 3],
            [0.5 * dt ** 2],
            [0.5 * dt ** 2],
            [dt],
            [dt],
        ]
    )
    return std_jrk ** 2 * G @ G.transpose()


def DYN_MAT_3D_CST_ACC_COV(dt, std_jrk):
    """TODO"""
    G = np.array(
        [
            [1.0 / 6.0 * dt ** 3],
            [1.0 / 6.0 * dt ** 3],
            [1.0 / 6.0 * dt ** 3],
            [0.5 * dt ** 2],
            [0.5 * dt ** 2],
            [0.5 * dt ** 2],
            [dt],
            [dt],
            [dt],
        ]
    )
    return std_jrk ** 2 * G @ G.transpose()


class Kalman:
    """Class to define a Kalman filter"""

    def __init__(
        self, F=None, Q=None, H=None, R=None, X0=None, P0=None, spreading=None, iter=1
    ):
        """Constructor of :class:`Kalman` class

        Unscented Kalman Filter is designed to perform non-linear and non-gaussian
        estimation on a sequence of unknown states, given a dynamic model F and an
        observation model H

        :param F: A function taking as input an [n x 1] state vector x(t) and returning
                  x(t+1), the prior mean of state vector at time t+1. If F is a matrix
                  transition is handled as standard KF or EKF.
        :param Q: The [n x n] state transition covariance matrix where
                  :math:`Qij = Cov(vi, vj)`, with: :math:`xi(t+1) = F(xi(t)) + vi`
        :param H: A function taking as input an [nx1] state vector x(t) and returning an
                  ``[m x 1]`` vector y(t), the observation vetcor at time t. If H is a matrix
                  observation is handled as a standard KF or EKF.
        :param R: The ``[m x m]`` state observation covariance matrix where
                  :math:`Rij = Cov(wi, wj)`,  with: :math:`yi(t) = H(xi(t)) + wi`
        :param X0: A :``[n x 1]`` initial state vector
        :param P0: A :``[n x n]`` initial state covariance matrix
        :param spreading: Parameter describing the distance between central mean and
                          sampled sigma points. As a default 2n+1 sigma points are
                          generated.
        :param iter: TODO
        """

        self.F = F
        self.Q = Q
        self.H = H
        self.R = R
        self.X0 = X0
        self.P0 = P0
        self.restart = None
        self.iter = iter
        self.control = 1
        self.spreading = 1

    def setTransition(self, F, Q=None):
        self.F = F
        if not Q is None:
            self.Q = Q

    def setObservation(self, H, R=None):
        self.H = H
        if not R is None:
            self.R = R

    def setInitState(self, X0, P0):
        self.X0 = X0
        if not P0 is None:
            self.P0 = P0

    def setSpreading(self, spreading):
        self.spreading = spreading

    def setRestart(self, restart):
        self.restart = restart

    def setIterations(self, iter):
        self.iter = iter

    def setInnovationControl(self, control):
        self.control = control

    def getQ(self, k, track):
        if not "function" in str(type(self.Q)):
            return self.Q
        else:
            if self.Q.__code__.co_argcount == 0:
                return self.Q()
            if self.Q.__code__.co_argcount == 1:
                return self.Q(k)
            if self.Q.__code__.co_argcount == 2:
                return self.Q(k, track)

    def getR(self, k, track):
        if not "function" in str(type(self.R)):
            return self.R
        else:
            if self.R.__code__.co_argcount == 0:
                return self.R()
            if self.R.__code__.co_argcount == 1:
                return self.R(k)
            if self.R.__code__.co_argcount == 2:
                return self.R(k, track)

    def summary(self):

        if ("function" in str(type(self.F))) or ("function" in str(type(self.H))):
            type_kalman = "unscented (UKF)"
        else:
            type_kalman = "standard (KF)"
        print("===========================================================")
        print("Kalman filter")
        print("Type:", type_kalman)
        t_dyn = "linear"
        t_obs = "linear"
        if type_kalman == "unscented (UKF)":
            if "function" in str(type(self.F)):
                t_dyn = "non-linear"
            if "function" in str(type(self.H)):
                t_obs = "non-linear"
            print("Dyn model:", t_dyn, "/ Obs model:", t_obs)
        stationarity = "Yes"
        if "function" in str(type(self.F)):
            if self.F.__code__.co_argcount > 1:
                stationarity = "No"
        if "function" in str(type(self.Q)):
            if self.Q.__code__.co_argcount > 0:
                stationarity = "No"
        if "function" in str(type(self.R)):
            if self.R.__code__.co_argcount > 0:
                stationarity = "No"
        print("Stationnarity:", stationarity)
        n = self.P0.shape[0]
        if "function" in str(type(self.R)):
            m = "?"
        else:
            m = self.R.shape[0]
        print("Number of states         n =", n)
        print("Number of observations   m =", m)
        print("===========================================================")
        print("Dynamic model [n x n]:")
        print(self.F)
        x = np.random.randint(0, 10, self.X0.shape)
        if t_dyn == "linear":
            y = (self.F @ x).transpose()
            print("E.g. x =", x.transpose(), "=>", "F(x) =", y)
        else:
            if self.F.__code__.co_argcount == 1:
                y = self.F(x).transpose()
                print("E.g. x =", x.transpose(), "=>", "F(x) =", y)
        print("-----------------------------------------------------------")
        print("Dynamic model covariance matrix [n x n]:")
        print(self.Q)
        print("===========================================================")
        print("Observation model [m x n]:")
        print(self.H)
        if m != "?":
            if t_obs == "linear":
                y = (self.H @ x).transpose()
                print("E.g. x =", x.transpose(), "=>", "H(x) =", y)
            else:
                if self.H.__code__.co_argcount == 1:
                    y = self.H(x).transpose()
                    print("E.g. x =", x.transpose(), "=>", "H(x) =", y)
        print("-----------------------------------------------------------")
        print("Observation model covariance matrix [m x m]:")
        print(self.R)
        print("===========================================================")
        print("Initial state vector [n x 1]")
        print(self.X0)
        print("-----------------------------------------------------------")
        print("Initial state covariance matrix [n x n]")
        print(self.P0)
        print("===========================================================")

    # ------------------------------------------------------------
    # Internal function to calculate sigma points.
    # Inputs:
    #    - mu : distribution mean vector
    #    - S: covariance matrix
    # ------------------------------------------------------------
    def __sampleSigmaPts(self, mu, S):

        n = mu.shape[0]

        # Cholesky decomposition
        L = np.linalg.cholesky((n + self.spreading) * S)

        # Sigma points computation
        X = np.concatenate([mu, mu + np.array([L[:, 0]]).transpose()], axis=1)

        for i in range(1, n):
            X = np.concatenate([X, mu + np.array([L[:, i]]).transpose()], axis=1)
        for i in range(n):
            X = np.concatenate([X, mu - np.array([L[:, i]]).transpose()], axis=1)
        return X

    # ------------------------------------------------------------
    # Internal function to calculate sigma point weights
    # ------------------------------------------------------------
    def __sampleSigmaWeights(self):
        n = self.X0.shape[0]
        l = self.spreading
        W = np.zeros((2 * n + 1, 1))
        W[0, 0] = l / (n + l)
        for i in range(1, 2 * n + 1):
            W[i, 0] = 1.0 / (2 * (n + l))
        return W

    # ------------------------------------------------------------
    # Internal function to calculate mean of sigma points
    # Inputs: sigma points matrix and weight vector
    # ------------------------------------------------------------
    def __mean(self, SIGMA, W):
        n = SIGMA.shape[0]
        M = np.zeros((n, 1))
        for i in range(SIGMA.shape[1]):
            M = M + W[i, 0] * np.array([SIGMA[:, i]]).transpose()
        return M

    # ------------------------------------------------------------
    # Internal function to calculate covariance of sigma points
    # Inputs: sigma points matrix and weight vector
    # ------------------------------------------------------------
    def __cov(self, SIGMA, W, M=None):
        n = SIGMA.shape[0]
        S = np.zeros((n, n))
        if M is None:
            M = self.__mean(SIGMA, W)
        for i in range(SIGMA.shape[1]):
            v = M - np.array([SIGMA[:, i]]).transpose()
            S = S + W[i, 0] * v @ v.transpose()
        return S

    # ------------------------------------------------------------
    # Internal function to calculate cross covariance Cov(X,Z)
    # Inputs: sigma points matrix and weight vector
    # ------------------------------------------------------------
    def __cross_cov(self, X, Z, W, MX=None, MZ=None):
        n = X.shape[0]
        m = Z.shape[0]
        T = np.zeros((n, m))
        if MX is None:
            MX = self.__mean(X, W)
        if MZ is None:
            MZ = self.__mean(Z, W)
        for i in range(X.shape[1]):
            vx = MX - np.array([X[:, i]]).transpose()
            vz = MZ - np.array([Z[:, i]]).transpose()
            T = T + W[i, 0] * vx @ vz.transpose()
        return T

    # ------------------------------------------------------------
    # Internal function to apply F or H to sigma points
    # ------------------------------------------------------------
    def __apply(self, function, SIGMA, k, track):
        if "function" in str(type(function)):
            if function.__code__.co_argcount == 1:
                output = function(np.array([SIGMA[:, 0]]).transpose())
                for i in range(1, SIGMA.shape[1]):
                    output = np.concatenate(
                        [output, function(np.array([SIGMA[:, i]]).transpose())], axis=1
                    )
            if function.__code__.co_argcount == 2:
                output = function(np.array([SIGMA[:, 0]]).transpose(), k)
                for i in range(1, SIGMA.shape[1]):
                    output = np.concatenate(
                        [output, function(np.array([SIGMA[:, i]]).transpose(), k)],
                        axis=1,
                    )
            if function.__code__.co_argcount == 3:
                output = function(np.array([SIGMA[:, 0]]).transpose(), k, track)
                for i in range(1, SIGMA.shape[1]):
                    output = np.concatenate(
                        [
                            output,
                            function(np.array([SIGMA[:, i]]).transpose(), k, track),
                        ],
                        axis=1,
                    )
        else:
            output = function @ np.array([SIGMA[:, 0]]).transpose()
            for i in range(1, SIGMA.shape[1]):
                output = np.concatenate(
                    [output, function @ np.array([SIGMA[:, i]]).transpose()], axis=1
                )

        return output

    # ------------------------------------------------------------
    # Internal function to get all observations at epoch k in a
    # track, from a list of analytical feature names (obs)
    # ------------------------------------------------------------
    def __getObs(self, track, obs, k, mode):
        return utils.unlistify(track.getObsAnalyticalFeatures(obs, k))

    # ------------------------------------------------------------
    # Main function of Kalman object, to estimate the states
    # Inputs:
    #   - track: the track on which estimation is performed
    #   - obs: the name of an analytical feature (may also a list
    #     of analytical feature names for multi-dimensional input)
    #     All the analytical features listed must be in the track
    #   - out: names of estimated fields as recorded in AF
    #   - mode: to specify how output states are used
    #        - MODE_STATES_AS_2D_POSITIONS: the first two
    #          fields of  output are used to make a Coords object
    #        - MODE_STATES_AS_2D_POSITIONS: the first three
    #          fields of  output are used to make a Coords object
    #     For MODE_STATES_AS_XX_POSITIONS modes, coordinates SRID
    #      is the same as track SRID.
    # ------------------------------------------------------------
    # Estimated parameters are registered in AF listed in out
    # and ("kf_0", "kf_1",..., "kf_n" otherwise if not provided).
    # Kalman gain matrix is saved at each epoch in "kf_gain" AF
    # Posterior covariance matrix Pk|k is saved in "kf_P" AF. It
    # may be used as it is to plot 2D error ellipses, provided
    # that first two states are x and y coordinates.
    # ------------------------------------------------------------
    def estimate(self, track, obs, out=[], mode=-1, verbose=True):

        if len(out) < self.X0.shape[0]:
            for i in range(len(out), self.X0.shape[0]):
                out.append("kf_" + str(i))

        # Output states
        for i in range(self.X0.shape[0]):
            track.createAnalyticalFeature(out[i], [0] * len(track))
        # Output states std values
        for i in range(self.X0.shape[0]):
            track.createAnalyticalFeature(out[i] + "_std", [0] * len(track))
        # Measurements innovation
        for i in range(len(obs)):
            track.createAnalyticalFeature("kf_" + obs[i] + "_inov", [0] * len(track))
            track.createAnalyticalFeature(
                "kf_" + obs[i] + "_inov_std", [0] * len(track)
            )

        # Matrices AF (gain and covariance matrix)
        track.createAnalyticalFeature("kf_gain", [0] * len(track))
        track.createAnalyticalFeature("kf_P", [0] * len(track))

        # Initialization
        W = self.__sampleSigmaWeights()

        X = self.X0
        P = self.P0
        I = np.eye(P.shape[0], P.shape[1])
        OUTPUT = []

        EPOCHS = range(len(track))
        if verbose:
            EPOCHS = progressbar.progressbar(EPOCHS)

        # Filter
        for k in EPOCHS:

            if not self.restart is None:
                self.restart(X, P, track, k)

            for step in range(self.iter):

                SIGMA_PTS = self.__sampleSigmaPts(X, P)

                # Prediction step
                if step == 0:
                    SIGMA_PTS = self.__apply(self.F, SIGMA_PTS, k, track)
                    MU = self.__mean(SIGMA_PTS, W)
                    COV = self.__cov(SIGMA_PTS, W, MU) + self.getQ(k, track)

                # Update step
                SIGMA_PTS2 = self.__apply(self.H, SIGMA_PTS, k, track)
                z = self.__getObs(track, obs, k, mode)
                Z = self.__mean(SIGMA_PTS2, W)
                I = np.array([z]).transpose() - Z
                S = self.__cov(SIGMA_PTS2, W, Z) + self.getR(k, track)

                # Innovation control
                if Stochastics.khi2test(I, S, self.control):
                    continue

                T = self.__cross_cov(SIGMA_PTS, SIGMA_PTS2, W, MU, Z)
                K = T @ np.linalg.inv(S)

                X = MU + K @ I
                P = COV - K @ S @ K.transpose()
                MU = X
                COV = P

            # Output states
            for i in range(X.shape[0]):
                track.setObsAnalyticalFeature(out[i], k, X[i, 0])
                track.setObsAnalyticalFeature(out[i] + "_std", k, math.sqrt(P[i, i]))

            # Measurement innovations
            for i in range(len(obs)):
                track.setObsAnalyticalFeature("kf_" + obs[i] + "_inov", k, I[i])
                track.setObsAnalyticalFeature(
                    "kf_" + obs[i] + "_inov_std", k, I[i] / S[i, i]
                )

            # Matrices AF
            track.setObsAnalyticalFeature("kf_gain", k, K)
            track.setObsAnalyticalFeature("kf_P", k, P)

        # MODE_STATES_AS_XX_POSITIONS
        if mode == MODE_STATES_AS_2D_POSITIONS:
            track.setXFromAnalyticalFeature(out[0])
            track.setYFromAnalyticalFeature(out[1])
        if mode == MODE_STATES_AS_3D_POSITIONS:
            track.setXFromAnalyticalFeature(out[0])
            track.setYFromAnalyticalFeature(out[1])
            track.setZFromAnalyticalFeature(out[2])


class HMM:
    """
    Hidden Markov Model is designed to estimate discrete
    sequential variables on tracks, given a probabilistic
    transition model Q and observation model P on S:

        - S is a two-valued function, where S(t, k)
            provides a list of all the possible states of
            track t at epoch k.
        - Q is a four-valued function, giving the (possibly
          non-normalized) probability function Q(s1,s2,k,t)
          to observe a transition from state s1 to state s2, at
          in track t at epoch k.
        - P is a four-valued function, giving the (possibly
          non-normalized) probability P(s,y,k,t) = P(y|si),
          the probability to observe y when (actual) state is
          s in track t at epoch k.

    Note that s1 and s2 arguments in transition Q must belong
    to the sets S(t,k) and S(t,k+1), respectively.
    Observation y may be  any value (continuous or discrete,
    even string or boolean). It may also be a list of values
    for multi-dimensional hidden markov model.
    If the underlying Markov model is stationnary, then
    Q, P and S do not depend on k. In this case, track t
    and epoch k are no longer mandatory in S, Q and P
    functions. They can be 0-valued (constant output),
    2-valued and 2-valued (respectively), if the boolean
    member value "stationarity" is set to True.
    log: set to True if Q and P are already log values"""

    def __init__(self, S=None, Q=None, P=None, log=False, stationarity=False):
        """TODO"""
        self.S = S
        self.P = P
        self.Q = Q
        self.log = log
        self.stationarity = stationarity

    def setLog(self, log):
        """TODO"""
        self.log = log

    def setStationarity(self, stat):
        """TODO"""
        self.stationarity = stat

    def setStates(self, S):
        """TODO"""
        self.S = S

    def setObservationModel(self, P):
        """TODO"""
        self.P = P

    def setTransitionModel(self, Q):
        """
        Set the transition model.
        
        :param Q: four-valued function, giving the probability function 
                  Q(s1,s2,k,t) to observe a transition from state s1 to state 
                  s2, at in track t at epoch k.
        """
        self.Q = Q

    def Qlog(self, s1, s2, k, track):
        """TODO"""
        q = self.Q(s1, s2, k, track)
        if not (self.log):
            q = math.log(q + 1e-300)
        return q

    def Plog(self, s, y, k, track):
        """TODO"""
        p = self.P(s, y, k, track)
        if not (self.log):
            p = math.log(p + 1e-300)
        return p

    def __getObs(self, track, obs, k, mode):
        """Internal function to get all observations at epoch k in a
        track, from a list of analytical feature names (obs) and a
        mode if retrieved values must be converted to positions

        TODO
        """

        y = track.getObsAnalyticalFeatures(obs, k)

        if mode in [MODE_OBS_AS_2D_POSITIONS, MODE_OBS_AND_STATES_AS_2D_POSITIONS]:
            if len(y) < 2:
                print("Error: wrong number of observations in HMM to form 2D position")
                exit()
            ytemp = [utils.makeCoords(y[0], y[1], 0.0, track.getSRID())]
            for remain in range(2, len(y)):
                ytemp.append(y[remain])
            y = ytemp
        if mode in [MODE_OBS_AS_3D_POSITIONS, MODE_OBS_AND_STATES_AS_3D_POSITIONS]:
            if len(y) < 3:
                print("Error: wrong number of observations in HMM to form 3D position")
                exit()
            ytemp = [utils.makeCoords(y[0], y[1], y[2], track.getSRID())]
            for remain in range(3, len(y)):
                ytemp.append(y[remain])
            y = ytemp

        return utils.unlistify(y)

    # Method to deal with computation trace
    def printTrace(self, message, importance, level):
        """TODO"""
        if level in importance:
            print(message)

    def printSeparator(self, importance, level, type):
        """TODO"""
        if level in importance:
            if type == 0:
                style = "--------------------------------------"
            if type == 1:
                style = "======================================"
            print(style + style)


    def estimate (self, track, obs, log=False, mode=MODE_OBS_AS_SCALAR,
                        verbose=MODE_VERBOSE_PROGRESS_BY_EPOCH):
        """
        Main function of HMM object, to estimate (decode) the
        maximum a posteriori sequence of states given observations
      
        Inputs:
        :param track: the track on which estimation is performed
        :param obs: the name of an analytical feature (may also a list
                    of analytical feature names for multi-dimensional HMM)
                    All the analytical features listed must be in the track
        :param mode: to specify how observations are used
                     - MODE_OBS_AS_SCALAR: list of values (default)
                     - MODE_OBS_AS_2D_POSITION: the first two fields
                       of  obs are used to make a Coords object.
                       Z component is set to 0 as default.
                     - MODE_OBS_AS_3D_POSITIONS: the first three fields
                       of obs are used to make a Coords object
                     For MODE_OBS_AS_2D_POSITIONS / MODE_OBS_AS_3D_POSITIONS
                     modes, coordinates SRID is the same as track SRID.
        :return: void
        """

        # -----------------------------------------------
        # Preprocessing
        # -----------------------------------------------
        self.printTrace("Compilation of states on track", [1, 2, 3], verbose)

        N = len(track)
        STATES = []
        for k in range(N):
            s = self.S(track, k)
            STATES.append(s)

        TAB_MRK = []
        TAB_VAL = []

        self.printTrace("Cost and marker matrix initialization", [1, 2, 3], verbose)
        
        for k in range(N):
            TAB_MRK.append([0] * len(STATES[k]))
            TAB_VAL.append([0] * len(STATES[k]))

        self.printTrace("Compilation of observations on track", [1, 2, 3], verbose)

        OBS = []
        for k in range(N):
            OBS.append(self.__getObs(track, obs, k, mode))

        for l in range(len(TAB_MRK[0])):
            TAB_MRK[0][l] = -1
            TAB_VAL[0][l] = -self.Plog(STATES[0][l], OBS[0], 0, track)
        
        # -----------------------------------------------
        # Forward step
        # -----------------------------------------------
        self.printTrace("Optimal sequence computation", [1, 2, 3], verbose)

        EPOCHS = range(1, N)
        if verbose == MODE_VERBOSE_PROGRESS:
            EPOCHS = progressbar.progressbar(EPOCHS)
            
        for k in EPOCHS:

            y = OBS[k]
            STATES_TO_TEST = range(len(TAB_MRK[k]))

            message = (
                "Epoch "
                + str(k + 1)
                + "/"
                + str((len(TAB_MRK)))
                + " ("
                + str(len(TAB_MRK[k]))
                + " states)"
            )
            self.printTrace(message, [1, 3], verbose)

            if verbose == MODE_VERBOSE_PROGRESS_BY_EPOCH:
                STATES_TO_TEST = progressbar.progressbar(STATES_TO_TEST)

            for l in STATES_TO_TEST:

                best_val = 1e300
                best_ant = 0
                s2 = STATES[k][l]
                s1 = STATES[k][l] # AJOUT MDVD
                for m in range(len(TAB_MRK[k - 1])):

                    s1 = STATES[k - 1][m]
                    q = -self.Qlog(s1, s2, k - 1, track)
                    val = q + TAB_VAL[k - 1][m]

                    message = (
                        "State " + str(l) + "/" + str(k - 1) + " " + str(s1) + " --> "
                    )
                    message += "state " + str(m) + "/" + str(k) + " " + str(s2)
                    message += " TRANSITION COST = " + str(q)
                    self.printTrace(message, [1], verbose)

                    if val < best_val:
                        best_val = val
                        best_ant = m

                p = -self.Plog(s2, y, k, track)
                TAB_MRK[k][l] = best_ant
                TAB_VAL[k][l] = best_val + p

                message = "State " + str(l) + "/" + str(k - 1) + " " + str(s1) + " to "
                message += str(y) + "  OBS COST = " + str(p)
                self.printTrace(message, [1], verbose)
                self.printSeparator([1], verbose, 0)

            self.printSeparator([1], verbose, 1)

        # -----------------------------------------------
        # Backward step
        # -----------------------------------------------
        self.printTrace("Backward reconstruction phase", [1, 2, 3], verbose)
        track.createAnalyticalFeature("hmm_inference")
        track.createAnalyticalFeature("hmm_cost")
        
        idk = np.argmin(TAB_VAL[-1])
        for k in range(N - 1, -1, -1):
            #if len(TAB_VAL[k]) == 0:
            #    continue
            
            self.printTrace(
                "Step "
                + str(k)
                + ": state "
                + str(idk)
                + " (cost: "
                + str(TAB_VAL[k][idk])
                + ")",
                [1],
                verbose,
            )
            track.setObsAnalyticalFeature("hmm_inference", k, STATES[k][idk])
            track.setObsAnalyticalFeature("hmm_cost", k, TAB_VAL[k][idk])
            if mode in [3, 4, 5]:
                track[k].position = STATES[k][idk]
            idk = TAB_MRK[k][idk]

        self.printSeparator([1], verbose, 1)
