"""
rayleigh_model.py
------------------
Utilidades para ajustar una distribución Rayleigh a una lista de muestras
(por ejemplo: conteos de defectos por proyecto). Proporciona una pequeña API
empleada por el script de entrenamiento y por el servidor API.

Funciones:
- fit_rayleigh(samples): devuelve la sigma (MLE), número de muestras y
    la media de los cuadrados.
- expected_value(sigma): esperanza de la Rayleigh.
- percentile(sigma, p): cuantiles de la Rayleigh.
- summary_from_samples(samples): resumen con métricas clave.

Notas:
- El estimador MLE usado es sigma_hat = sqrt( (1/(2n)) * sum(x_i^2) ).
- Tratamos los conteos como floats para la fórmula; si se necesita un
    modelado discreto riguroso, considerar Poisson o Binomial Negativa.
"""

import math
from typing import Sequence, Tuple


def fit_rayleigh(samples: Sequence[float]) -> Tuple[float, int, float]:
    """Ajusta la distribución Rayleigh por máxima verosimilitud.

    Args:
        samples: iterable de valores no negativos (ej. conteos de defectos por proyecto).

    Devuelve:
        (sigma, n_samples, mean_sq)

    Lanza:
        ValueError si la lista de muestras está vacía.
    """
    # Convert to float and validate
    xs = [float(x) for x in samples]
    n = len(xs)
    if n == 0:
        raise ValueError("No samples provided")

    # Mean square and MLE for sigma
    mean_sq = sum(x * x for x in xs) / n
    sigma = math.sqrt(mean_sq / 2.0)
    return sigma, n, mean_sq


def pdf(x: float, sigma: float) -> float:
    """Densidad de probabilidad de Rayleigh.

    PDF: f(x; sigma) = (x / sigma^2) * exp(-x^2 / (2 sigma^2)) para x >= 0.
    Devuelve 0 si x < 0.
    """
    if x < 0:
        return 0.0
    return (x / (sigma * sigma)) * math.exp(- (x * x) / (2.0 * sigma * sigma))


def cdf(x: float, sigma: float) -> float:
    """Función de distribución acumulada de Rayleigh.

    CDF: F(x; sigma) = 1 - exp(-x^2 / (2 sigma^2)) para x >= 0.
    Devuelve 0 si x < 0.
    """
    if x < 0:
        return 0.0
    return 1.0 - math.exp(- (x * x) / (2.0 * sigma * sigma))


def logpdf(x: float, sigma: float) -> float:
    """Logaritmo de la densidad (útil para verosimilitud).

    Para x < 0 el valor está indefinido (retornamos -inf).
    """
    if x < 0:
        return float('-inf')
    return math.log(x) - 2.0 * math.log(sigma) - (x * x) / (2.0 * sigma * sigma)


def log_likelihood(samples: Sequence[float], sigma: float) -> float:
    """Log-verosimilitud de una muestra dada una sigma.

    L(sigma) = sum_i log f(x_i; sigma). Se usa para diagnóstico o para
    derivar el estimador MLE (ver Unidad 3.pdf entregada por el usuario).
    """
    xs = [float(x) for x in samples]
    return sum(logpdf(x, sigma) for x in xs)


def fit_mle(samples: Sequence[float]) -> Tuple[float, int, float]:
    """Alias explícito que indica que el ajuste usa MLE.

    A partir de la derivación del logaritmo de verosimilitud (ver PDF
    "Unidad 3"), el estimador por máxima verosimilitud para sigma es:

        sigma_hat = sqrt( (1 / (2 n)) * sum_{i=1}^n x_i^2 ).

    Esta función devuelve (sigma_hat, n, mean_sq) idéntico a `fit_rayleigh`.
    """
    return fit_rayleigh(samples)


def expected_value(sigma: float) -> float:
    """Devuelve la esperanza de la Rayleigh: E[X] = sigma * sqrt(pi/2)."""
    return sigma * math.sqrt(math.pi / 2.0)


def percentile(sigma: float, p: float) -> float:
    """Devuelve el cuantíl p (0 < p < 1) para la Rayleigh.

    Fórmula: q(p) = sigma * sqrt(-2 * ln(1 - p)).
    """
    if not (0 < p < 1):
        raise ValueError("p must be in (0,1)")
    return sigma * math.sqrt(-2.0 * math.log(1.0 - p))


def summary_from_samples(samples: Sequence[float]) -> dict:
    """Resumen de conveniencia (sigma, n, mean_sq, expected, p90, p95)."""
    sigma, n, mean_sq = fit_rayleigh(samples)
    return {
        "sigma": sigma,
        "n_samples": n,
        "mean_sq": mean_sq,
        "expected": expected_value(sigma),
        "p90": percentile(sigma, 0.9),
        "p95": percentile(sigma, 0.95)
    }
