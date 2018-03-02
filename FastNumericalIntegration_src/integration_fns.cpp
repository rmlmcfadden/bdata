/* List of functions for which we integrate numerically 
 * Derek Fujimoto
 * October 2017
 */ 

#ifndef INTEGRATION_FNS_CPP
#define INTEGRATION_FNS_CPP

#include <math.h>
#include "DEIntegrator.h"

// ========================================================================= //
// Stretched exponential class for integration
class StrExp
{
    public:
        double lambda;      // 1/T1
        double beta;        // beta
        double lifetime;    // probe lifetime 
        double t;           // time
    
        // Constructor
        StrExp(double t1,double lambda1,double beta1,double probelife)
        {
            lambda = lambda1;
            beta = beta1;
            lifetime = probelife;
            t = t1;
        }
    
        // Calculator
        double operator()(double tprime) const
        {
            return exp((tprime-t)/lifetime)*exp(-pow((t-tprime)*lambda,beta));
        }
};

// ========================================================================= //
// Stretched exponential class for integration
class MixedStrExp
{
    public:
        double lambda1;      // 1/T1
        double beta1;        // beta
        double lambda2;      // 1/T1
        double beta2;        // beta
        double alpha;       // mixing parameter
        double lifetime;    // probe lifetime 
        double t;           // time
    
        // Constructor
        MixedStrExp(double t1,double lambda11,double beta11,double lambda21,
                double beta21,double alpha1, double probelife)
        {
            lambda1 = lambda11;
            lambda2 = lambda21;
            beta1 = beta11;
            beta2 = beta21;
            alpha = alpha1;
            lifetime = probelife;
            t = t1;
        }
    
        // Calculator
        double operator()(double tprime) const
        {
            return exp((tprime-t)/lifetime)*
                    (alpha*exp(-pow((t-tprime)*lambda1,beta1))+
                    (1-alpha)*exp(-pow((t-tprime)*lambda2,beta2)));
        }
};

// ========================================================================= //
// Integral of stretched exponential from 0 to x
class IntegralStrExp
{
    public:
        double out;
        IntegralStrExp(double t, double tprime, double l, double b, double life)
        {
            out = DEIntegrator<StrExp>::Integrate(StrExp(t,l,b,life),0,tprime,1e-6);
        }
};

// ========================================================================= //
// Integral of stretched exponential from 0 to x
class IntegralMixedStrExp
{
    public:
        double out;
        IntegralMixedStrExp(double t, double tprime, double l1, double b1, 
                double l2, double b2, double a, double life)
        {
            out = DEIntegrator<MixedStrExp>::Integrate(MixedStrExp(t,l1,b1,l2,
                    b2,a,life),0,tprime,1e-6);
        }
};

    
#endif // INTEGRATION_FNS_CPP
