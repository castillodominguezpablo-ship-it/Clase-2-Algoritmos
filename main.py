from __future__ import annotations
import time
import random
import argparse
from typing import List, Optional

class NReinas:
    ""
    Resolver del problema de las N-Reinas.
    Representación: vector de tamaño n donde el índice es la columna y el valor la fila.
    """

    def __init__(self, n: int, seed: Optional[int] = None) -> None:
        if n < 1:
            raise ValueError("n debe ser >= 1")
        self.n: int = n
        self.soluciones: List[List[int]] = []
        if seed is not None:
            random.seed(seed)

    def limpiar(self) -> None:
        """Limpia las soluciones almacenadas."""
        self.soluciones.clear()

    def es_valida(self, solucion: List[int], fila: int, columna: int) -> bool:
        """Comprueba si colocar una reina en (fila, columna) es válido respecto a columnas previas."""
        for col in range(columna):
            if solucion[col] == fila or abs(solucion[col] - fila) == abs(col - columna):
                return False
        return True

    def resolver(self) -> None:
        """Encuentra todas las soluciones por backtracking y las almacena en self.soluciones."""
        self.limpiar()
        solucion = [-1] * self.n
        self._backtrack(0, solucion)

    def _backtrack(self, columna: int, solucion: List[int]) -> None:
        if columna == self.n:
            self.soluciones.append(solucion.copy())
            return
        for fila in range(self.n):
            if self.es_valida(solucion, fila, columna):
                solucion[columna] = fila
                self._backtrack(columna + 1, solucion)
                solucion[columna] = -1  # deshacer

    # --------- Enfoque probabilista (min-conflicts) para hallar UNA solución rápida ----------
    def conflictos_en(self, solucion: List[int], columna: int, fila: int) -> int:
        """Cuenta conflictos de ubicar (columna -> fila) respecto al resto de columnas."""
        conflictos = 0
        for c in range(self.n):
            if c == columna:
                continue
            f = solucion[c]
            if f == -1:
                continue
            if f == fila or abs(f - fila) == abs(c - columna):
                conflictos += 1
        return conflictos

    def resolver_probabilista(self, max_pasos: int = 10_000, reinicios: int = 50) -> Optional[List[int]]:
        """
        Min-conflicts: intenta hallar una solución válida (no garantiza todas).
        Devuelve una solución o None si no encontró en los reinicios dados.
        """
        for _ in range(reinicios):
            solucion = [random.randrange(self.n) for _ in range(self.n)]
            for _ in range(max_pasos):
                conflicted_cols = [c for c in range(self.n) if self.conflictos_en(solucion, c, solucion[c]) > 0]
                if not conflicted_cols:
                    return solucion.copy()
                col = random.choice(conflicted_cols)
                # Mover a la fila con menos conflictos (romper empates al azar)
                mejor_filas: List[int] = []
                mejor_conf: Optional[int] = None
                for fila in range(self.n):
                    conf = self.conflictos_en(solucion, col, fila)
                    if mejor_conf is None or conf < mejor_conf:
                        mejor_conf = conf
                        mejor_filas = [fila]
                    elif conf == mejor_conf:
                        mejor_filas.append(fila)
                solucion[col] = random.choice(mejor_filas)
        return None

    # --------------------- Utilidades ---------------------
    def cantidad_soluciones(self) -> int:
        return len(self.soluciones)

    def tablero_str(self, solucion: List[int]) -> str:
        """Devuelve una representación ASCII del tablero para una solución."""
        filas = []
        for r in range(self.n):
            fila = "".join("Q " if solucion[c] == r else ". " for c in range(self.n))
            filas.append(fila.rstrip())
        return "\n".join(filas)

def ejecutar_experimento(n_vals = range(4, 9)) -> None:
    """Ejecuta backtracking para n=4..8, imprime si existe solución, #soluciones y tiempo."""
    print("🧠 Resultados N-Reinas (backtracking)\n")
    print(f"{'n':>2}  {'¿Existe?':>9}  {'#Soluciones':>12}  {'Tiempo (s)':>10}")
    print("-" * 40)
    for n in n_vals:
        solver = NReinas(n)
        t0 = time.perf_counter()
        solver.resolver()
        t1 = time.perf_counter()
        existe = "Sí" if solver.cantidad_soluciones() > 0 else "No"
        print(f"{n:>2}  {existe:>9}  {solver.cantidad_soluciones():>12}  {t1 - t0:>10.4f}")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolver N-Reinas (backtracking y min-conflicts).")
    parser.add_argument("--experimento", action="store_true", help="Ejecuta la tabla para n=4..8 con backtracking.")
    parser.add_argument("-n", "--n", type=int, default=8, help="Tamaño del tablero (por defecto 8).")
    parser.add_argument("--seed", type=int, default=None, help="Semilla para aleatoriedad (opcional).")
    parser.add_argument("--metodo", choices=["backtracking", "probabilista"], default="backtracking",
                        help="Método de resolución.")
    parser.add_argument("--mostrar-soluciones", action="store_true", help="Imprime soluciones encontradas.")
    parser.add_argument("--mostrar-tablero", action="store_true", help="Imprime tablero ASCII de las soluciones.")
    parser.add_argument("--limite-impresion", type=int, default=5, help="Máx. soluciones a imprimir.")
    parser.add_argument("--max-pasos", type=int, default=10_000, help="Máx. pasos para min-conflicts.")
    parser.add_argument("--reinicios", type=int, default=50, help="Reinicios aleatorios para min-conflicts.")
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    if args.experimento:
        ejecutar_experimento()
        return

    solver = NReinas(args.n, seed=args.seed)

    if args.metodo == "backtracking":
        t0 = time.perf_counter()
        solver.resolver()
        t1 = time.perf_counter()
        print(f"n={args.n}: {solver.cantidad_soluciones()} soluciones en {t1 - t0:.4f}s")
        if args.mostrar_soluciones:
            to_show = solver.soluciones[: max(0, args.limite_impresion)]
            for i, sol in enumerate(to_show, 1):
                print(f"- Solución {i}: {sol}")
                if args.mostrar_tablero:
                    print(solver.tablero_str(sol), "\n")
    else:
        t0 = time.perf_counter()
        sol = solver.resolver_probabilista(max_pasos=args.max_pasos, reinicios=args.reinicios)
        t1 = time.perf_counter()
        if sol:
            print(f"Solución probabilista encontrada para n={args.n} en {t1 - t0:.4f}s:")
            print(sol)
            if args.mostrar_tablero:
                print(solver.tablero_str(sol))
        else:
            print(f"No se encontró solución probabilista para n={args.n} (tiempo {t1 - t0:.4f}s).")

if __name__ == "__main__":
    main()