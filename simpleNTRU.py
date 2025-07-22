# Simple NTRU implementation in Python using SageMath
# !!!FOR EDUCATIONAL PURPOSES ONLY - NOT CRYPTOGRAPHICALLY SECURE!!!

from sage.all import *
import random

class SimpleNTRU:

    def __init__(self, N=11, p=3, q=32):
        """
        Initialize NTRU parameters
        N: polynomial degree
        p: small modulus (usually 3)
        q: large modulus (should be power of 2, q >> p)
        """
        self.N = N
        self.p = p
        self.q = q
        
        # Define polynomial ring Z[x]/(x^N - 1)
        R = PolynomialRing(ZZ, 'x')
        x = R.gen()
        self.R = R
        self.x = x
        
        # Define quotient rings
        self.Rp = R.quotient(x**N - 1)
        
    def random_small_poly(self, d1, d2):
        """
        Generate a random small polynomial with d1 coefficients = 1,
        d2 coefficients = -1, and the rest = 0
        """
        coeffs = [0] * self.N
        
        # Place d1 ones
        positions = random.sample(range(self.N), d1 + d2)
        for i in range(d1):
            coeffs[positions[i]] = 1
        
        # Place d2 minus ones
        for i in range(d1, d1 + d2):
            coeffs[positions[i]] = -1
            
        return self.R(coeffs)
    
    def poly_mod_q(self, poly):
        """Reduce polynomial coefficients modulo q"""
        coeffs = poly.coefficients(sparse=False)
        if len(coeffs) < self.N:
            coeffs.extend([0] * (self.N - len(coeffs)))
        
        new_coeffs = list(map(lambda t: t % self.q, coeffs[:self.N]))
        return self.R(new_coeffs)
    
    def poly_mod_p(self, poly):
        """Reduce polynomial coefficients modulo p"""
        coeffs = poly.coefficients(sparse=False)
        if len(coeffs) < self.N:
            coeffs.extend([0] * (self.N - len(coeffs)))
        
        new_coeffs = list(map(lambda t: t % self.p, coeffs[:self.N]))
        return self.R(new_coeffs)
    
    def poly_reduce(self, poly):
        """Reduce polynomial modulo (x^N - 1)"""
        coeffs = poly.coefficients(sparse=False)
        reduced_coeffs = [0] * self.N
        
        for i, coeff in enumerate(coeffs):
            reduced_coeffs[i % self.N] += coeff
            
        return self.R(reduced_coeffs)
    
    def poly_mult_mod(self, a, b, mod):
        """Multiply polynomials and reduce modulo (x^N - 1) and coefficients modulo mod"""
        product = a * b
        reduced = self.poly_reduce(product)
        
        if mod == self.p:
            return self.poly_mod_p(reduced)
        elif mod == self.q:
            return self.poly_mod_q(reduced)
        else:
            return reduced
    
    def inv_poly(self, poly, modulus):
        """Compute the the inverse of the polynomial in the polynomial ring"""
        try:
            Rm = PolynomialRing(Integers(modulus), 'x')
            x = Rm.gen()
            ideal = Rm.ideal(x**self.N - 1)
            quotient_ring = Rm.quotient(ideal)

            poly_coeffs = poly.coefficients(sparse=False)
            if len(poly_coeffs) < self.N:
                poly_coeffs.extend([0] * (self.N - len(poly_coeffs)))
            poly_in_quotient = quotient_ring(Rm(poly_coeffs[:self.N]))

            return poly_in_quotient**(-1)
        except:
            return None

    def keygen(self):
        """Generate NTRU key pair"""
        print("Generating NTRU keys...")
        
        # Choose small polynomials f and g
        # f should be invertible modulo p and q
        d = self.N // 3  # Number of ±1 coefficients
        
        # Generate f with d+1 ones and d negative ones (to ensure invertibility)
        f = self.random_small_poly(d + 1, d)
        g = self.random_small_poly(d, d)
        
        print(f"f = {f}")
        print(f"g = {g}")
        
        # Find f^(-1) mod p and f^(-1) mod q
        fp_inv = self.inv_poly(f, self.p)
        fq_inv = self.inv_poly(f, self.q)
        
        if fp_inv is None or fq_inv is None:
            print("Failed to find inverse, trying again...")
            return self.keygen()  # Recursive retry
        
        # Convert back to our polynomial ring
        fp_inv_coeffs = list(fp_inv)[:self.N]
        fq_inv_coeffs = list(fq_inv)[:self.N]
        
        fp_inv = self.R(fp_inv_coeffs)
        fq_inv = self.R(fq_inv_coeffs)
        
        print(f"f^(-1) mod p = {fp_inv}")
        print(f"f^(-1) mod q = {fq_inv}")
        
        # Compute public key h = p * fq_inv * g (mod q)
        h = self.poly_mult_mod(self.p * fq_inv, g, self.q)
        
        print(f"Public key h = {h}")
        
        # Private key is (f, fp_inv)
        private_key = (f, fp_inv)
        public_key = h
        
        return private_key, public_key
    
    def encrypt(self, message, public_key):
        """Encrypt a message using NTRU"""
        h = public_key
        
        # Convert message to polynomial (coefficients should be in {0, 1, ..., p-1})
        if isinstance(message, str):
            # Simple encoding: use ASCII values mod p
            message_coeffs = [ord(c) % self.p for c in message[:self.N]]
            if len(message_coeffs) < self.N:
                message_coeffs.extend([0] * (self.N - len(message_coeffs)))
        else:
            message_coeffs = message
        
        m = self.R(message_coeffs)
        print(f"Message polynomial m = {m}")
        
        # Choose random small polynomial r
        d = self.N // 3
        r = self.random_small_poly(d, d)
        print(f"Random polynomial r = {r}")
        
        # Compute ciphertext c = r * h + m (mod q)
        c = self.poly_mult_mod(r, h, self.q)
        c = self.poly_mod_q(c + m)
        
        print(f"Ciphertext c = {c}")
        return c
    
    def decrypt(self, ciphertext, private_key):
        """Decrypt a ciphertext using NTRU"""
        f, fp_inv = private_key
        c = ciphertext
        
        # Compute a = f * c (mod q)
        a = self.poly_mult_mod(f, c, self.q)
        print(f"f * c mod q = {a}")
        
        # Center coefficients of a (bring to range [-q/2, q/2))
        a_coeffs = a.coefficients(sparse=False)
        if len(a_coeffs) < self.N:
            a_coeffs.extend([0] * (self.N - len(a_coeffs)))
        
        centered_coeffs = []
        for coeff in a_coeffs[:self.N]:
            if coeff > self.q // 2:
                centered_coeffs.append(coeff - self.q)
            else:
                centered_coeffs.append(coeff)
        
        a_centered = self.R(centered_coeffs)
        print(f"Centered a = {a_centered}")
        
        # Compute b = a mod p
        b = self.poly_mod_p(a_centered)
        print(f"b = a mod p = {b}")
        
        # Recover message m = fp_inv * b (mod p)
        m = self.poly_mult_mod(fp_inv, b, self.p)
        print(f"Recovered message m = {m}")
        
        return m

# Example usage
def main():
    print("=== Simple NTRU Example ===\n")
    
    # Initialize NTRU with small parameters
    ntru = SimpleNTRU(N=11, p=3, q=32)
    
    # Generate keys
    private_key, public_key = ntru.keygen()
    print(f"\n=== Key Generation Complete ===")
    print(f"Private key: f = {private_key[0]}")
    print(f"             f^(-1) mod p = {private_key[1]}")
    print(f"Public key:  h = {public_key}")
    
    # Encrypt a message
    print(f"\n=== Encryption ===")
    message = [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0]  # Binary message
    print(f"Original message: {message}")
    
    ciphertext = ntru.encrypt(message, public_key)
    print(f"Encryption complete!")
    
    # Decrypt the message
    print(f"\n=== Decryption ===")
    recovered = ntru.decrypt(ciphertext, private_key)
    
    print(f"\n=== Results ===")
    print(f"Original message:  {message}")
    print(f"Recovered message: {recovered.coefficients(sparse=False)}")
    
    # Check if decryption was successful
    recovered_coeffs = recovered.coefficients(sparse=False)
    if len(recovered_coeffs) < len(message):
        recovered_coeffs.extend([0] * (len(message) - len(recovered_coeffs)))
    
    if message == recovered_coeffs[:len(message)]:
        print("✅ Decryption successful!")
    else:
        print("❌ Decryption failed!")

if __name__ == "__main__":
    main()
