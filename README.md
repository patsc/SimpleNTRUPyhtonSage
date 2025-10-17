# Simple Implementation of NTRU in Python and Sage

Simple implementation of the NTRU cryptosystem in Python and SageMath for educational purposes.

*The implementation is intended to be used for educational purposes only, i.e., it is by no means cryptographically secure and should not be used for any real world implementation.*

## Description

[NTRU](https://www.ntru.org) is an efficient, lattice-based public key encryption scheme that uses polynomial rings. Originally proposed as a trapdoor one-way function, it can be transformed into a Chosen-Ciphertext-Attacker (CCA) secure encryption scheme.

The scheme and implementation presented here is a kind of "school-book" variant of the scheme and should not be used in realworld applications.

### Building Blocks

#### Polynomial-Ring

For a given integer $q$, let $\mathcal{R}_q$ denote the ring $\mathbb{Z}_q$, i.e., the ring of integers modulo $q$. For a monic polynomial $f\in\mathbb{Z}_q[x]$ of degree $n$, $\mathcal{R}_{q,f}$ denotes the polynomial ring $\mathbb{Z}_q[x]/ f(x)$.

For $\beta$ sufficiently small (we will see below what we mean by "sufficiently small") let $[\beta] := \{-\beta, -\beta +1, ... , -1, 0, 1, ..., \beta\}$. For a polynomial $p$, we denote by $p \leftarrow [\beta]$ the fact that the coefficients of $p$ have been chosen uniformly at random from $[\beta]$.

#### Generalized LWE Problem

For NTRU we consider the *search* version of the Learning with Error (LWE) problem. I.e., given $(a,a\cdot s +e)$ for a random elements $a \leftarrow \mathcal{R}_{q,f}$ and $s,e \leftarrow [\beta]$, the task is to find $s$ and $e$.

For completion, the *decision* version of the problem requires to distinguish $(a,u)$ from $(a,a\cdot s +e)$ for $a,u \leftarrow \mathcal{R}_{q,f}$ and $e,s \leftarrow [\beta]$. 

#### Parameters

To instantiate the encryption scheme, we choose two integers $q$ and $p$ relatively prime, where $q$ is larger than $p$. Typically, $q$ is a power of $2$, $p$ is set to $3$, furthermore $p = 2\cdot \beta +1$, i.e., $[\beta ] = \{-1, 0, 1\}$.

We furthermore choose a parameter $d$ that determines the number of non-zero coefficients of the polynomial elements that determine the key material of the scheme. For correctness of the scheme, we will require that $q$ and $d$ meet a relation that is explained below. 

For NTRU the corresponding LWE problem is defined as:
- let $p = 2\cdot \beta + 1$
- choose polynomials $f,g,e,s\in [\beta]$, such that $f$ has an inverse $f_q^{-1}$ in $\mathcal{R}_{q,x^n-1}$ as well as an inverse $f_p^{-1}$ in $\mathcal{R}_{p,x^n-1}$ and set $a=p\cdot f_q^{-1}\cdot g$
- for given $(a,a\dot s +e)$ find $e$ and $s$

#### The Public and Private Key

For parameters $p$, $q$ and polynomials $f$ and $g$ as defined in the previous section, the *public key* is defined as $p_k := p \cdot f_q^{-1} \cdot g \in \mathcal{R}_{q,x^n-1}$.

The corresponding *private key* is $f$.

#### Encryption and Decryption

*Encryption*: 

The cleartext message is encoded as a small polynomial $m$ in $\mathcal{R}_{x^n-1}$, i.e., the coefficients of $m$ are in $[\beta]$.

To encrypt $m$ the sender furthermore creates a random polynomial $r \in \mathcal{R}_{q,x^n-1}$, where again the coefficients of $r$ are small ($m\in [\beta]$).

The ciphertext is then computed as: $c = pk \cdot r + m = p\cdot f_q^{-1} \cdot g \cdot r + m \in \mathcal{R}_{q,x^n -1}$ 

*Decryption*:

For decryption the receiver uses his private key $f$ and multiplies it with the cipher text: $f \cdot c = f\cdot p \cdot f_q^{-1} \cdot g \cdot r + f \cdot m$. Before we start, however, we move all coefficients into the interval $[- q/2, q/2]$. This step is necessary, since we have encoded our message and have defined our polynomials in this domain.

Note that multiplication is done in $\mathcal{R}_{q,x^n-1}$, thus $f$ and $f_q^{-1}$ cancle out and we are left with $p \cdot g \cdot r + f\cdot m$. We would now like to work modulo $p$, but need to be careful not to introduce failures, since we apply modulo $q$ and modulo $p$ in a certain order. In general, this may lead to problems, however, if reduction modulo $q$ does not change any parameter (coefficient), we are fine.

Looking at the polynomials and their coefficients (taken from $[\beta]$), and using the fact that we set $p=3$, thus $\beta =1$, and the fact that our polynomials have at most $2\cdot d$ non-zero coefficients, we know that the coefficents cannot exceed $3 \cdot 2\cdot d + 2 \cdot d$. As a consequence, if we require $q/2 > 8 \cdot d$ we have a guarantee that reduction modulo $q$ does not change any of the coefficients and that we are fine.

In the next step, we multiple with $f_p^{-1}$ and reduce module $p$ such that the remaining term corresponds to the cleartext $m$.








