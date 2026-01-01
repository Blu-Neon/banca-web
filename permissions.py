"""Permessi applicazione (bitmask).

Regola: ogni permesso singolo DEVE essere una potenza di 2 (1,2,4,8,...).
Così puoi combinarli in un unico intero (es: PRO|XMAS = 3).
"""

# Permessi base
PERM_PRO = 1            # non ancora utilizzato 
PERM_XMAS = 2           # biglietto di natale
PERM_ADMIN = 4          # il mio 
PERM_MEDIA = 8          # profilo social 
PERM_PROGRAMMER = 16    # aiuto nello sviluppo 


def has_perm(user_perms: int | None, perm: int) -> bool:
    """Ritorna True se user_perms contiene il perm richiesto."""
    p = int(user_perms or 0)
    return (p & perm) == perm
