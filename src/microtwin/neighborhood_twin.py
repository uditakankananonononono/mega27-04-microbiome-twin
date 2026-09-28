"""Research-only assemblage-neighborhood correction to a population prior.

The rule is frozen in results/PREREG_20260928_neighbor_trust_twin.md.
It uses only query presence, never query abundance or a perturbation outcome.
"""
import numpy as np


class NeighborhoodTrustTwin:
    def fit(self, z, p):
        z = np.asarray(z, dtype=float)
        p = np.asarray(p, dtype=float)
        if z.ndim != 2 or p.shape != z.shape or not len(z) or not np.isfinite(z).all() or not np.isfinite(p).all():
            raise ValueError('finite nonempty aligned training matrices required')
        if (z < 0).any() or (p < 0).any() or (p.sum(1) <= 0).any() or ((p > 0) & (z <= 0)).any():
            raise ValueError('invalid abundance, assemblage or support')
        self.z = z > 0
        self.p = p / p.sum(1, keepdims=True)
        self.mean = self.p.mean(0)
        return self

    def predict_with_details(self, z):
        q = np.asarray(z, dtype=float)
        if q.ndim != 2 or q.shape[1] != self.z.shape[1] or not np.isfinite(q).all() or (q < 0).any() or (q.sum(1) <= 0).any():
            raise ValueError('finite, nonempty, aligned query assemblages required')
        present = q > 0
        if (present & (self.mean <= 0)).any():
            raise ValueError('present query taxon absent in training; abstaining')
        intersection = present.astype(float) @ self.z.astype(float).T
        union = present.sum(1)[:, None] + self.z.sum(1)[None, :] - intersection
        similarity = np.divide(intersection, union, out=np.zeros_like(intersection), where=union > 0)
        weight = similarity ** 4
        weight_sum = weight.sum(1)
        weight_sq = (weight ** 2).sum(1)
        neff = np.divide(weight_sum ** 2, weight_sq, out=np.zeros_like(weight_sum), where=weight_sq > 0)
        local = weight @ self.p
        local *= present
        local_sum = local.sum(1)
        prior = present * self.mean
        prior /= prior.sum(1, keepdims=True)
        good = local_sum > 0
        local[good] /= local_sum[good, None]
        local[~good] = prior[~good]
        alpha = (neff / (neff + 5)) * similarity.max(1) ** 2
        alpha[~good] = 0
        pred = (1 - alpha[:, None]) * prior + alpha[:, None] * local
        return pred, {'prior': prior, 'local': local, 'alpha': alpha,
                      'effective_neighbors': neff, 'fallback': ~good}

    def predict(self, z):
        return self.predict_with_details(z)[0]
