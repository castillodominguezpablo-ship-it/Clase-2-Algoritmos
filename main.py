from __future__ import annotations
import time
import random
import argparse
from typing import List, Optional

class NReinas:
    """
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

def _imprimir_soluciones(solver: "NReinas", mostrar_soluciones: bool, mostrar_tablero: bool, limite: int) -> None:
    if not mostrar_soluciones:
        return
    if limite is not None and limite > 0:
        to_show = solver.soluciones[:limite]
    else:
        to_show = solver.soluciones
    for i, sol in enumerate(to_show, 1):
        print(f"- Solución {i}: {sol}")
        if mostrar_tablero:
            print(solver.tablero_str(sol), "\n")


def ejecutar_experimento(
    n_inicio: int = 4,
    n_fin: int = 8,
    *,
    mostrar_soluciones: bool = False,
    mostrar_tablero: bool = False,
    limite_impresion: int = 0,
) -> None:
    """Ejecuta backtracking para n en [n_inicio..n_fin].
    Puede opcionalmente imprimir las soluciones y tableros (si limite_impresion <=0, imprime todas).
    """
    if n_inicio < 1 or n_fin < 1 or n_inicio > n_fin:
        raise ValueError("Rango inválido: asegúrate de que 1 <= n_inicio <= n_fin")
    print("🧠 Resultados N-Reinas (backtracking)\n")
    print(f"Rango: n={n_inicio}..{n_fin}")
    print(f"{'n':>2}  {'¿Existe?':>9}  {'#Soluciones':>12}  {'Tiempo (s)':>10}")
    print("-" * 40)
    for n in range(n_inicio, n_fin + 1):
        solver = NReinas(n)
        t0 = time.perf_counter()
        solver.resolver()
        t1 = time.perf_counter()
        existe = "Sí" if solver.cantidad_soluciones() > 0 else "No"
        print(f"{n:>2}  {existe:>9}  {solver.cantidad_soluciones():>12}  {t1 - t0:>10.4f}")
        _imprimir_soluciones(solver, mostrar_soluciones, mostrar_tablero, limite_impresion)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolver N-Reinas (backtracking y min-conflicts).")
    parser.add_argument("--experimento", action="store_true", help="Ejecuta la tabla para n=4..8 con backtracking.")
    parser.add_argument("--n-inicio", type=int, default=4, help="Valor inicial de n para el experimento (incluido).")
    parser.add_argument("--n-fin", type=int, default=8, help="Valor final de n para el experimento (incluido).")
    parser.add_argument("-n", "--n", type=int, default=8, help="Tamaño del tablero (por defecto 8).")
    parser.add_argument("--seed", type=int, default=None, help="Semilla para aleatoriedad (opcional).")
    parser.add_argument("--metodo", choices=["backtracking", "probabilista"], default="backtracking",
                        help="Método de resolución.")
    parser.add_argument("--mostrar-soluciones", action="store_true", help="Imprime soluciones encontradas.")
    parser.add_argument("--mostrar-tablero", action="store_true", help="Imprime tablero ASCII de las soluciones.")
    parser.add_argument("--limite-impresion", type=int, default=5, help="Máx. soluciones a imprimir (<=0 = todas).")
    parser.add_argument("--max-pasos", type=int, default=10_000, help="Máx. pasos para min-conflicts.")
    parser.add_argument("--reinicios", type=int, default=50, help="Reinicios aleatorios para min-conflicts.")
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    if args.experimento:
        # Validar y ejecutar experimento en rango
        if args.n_inicio < 1 or args.n_fin < 1 or args.n_inicio > args.n_fin:
            print("Error: rango inválido. Usa valores positivos y asegúrate de que n-inicio <= n-fin.")
            return
        ejecutar_experimento(
            args.n_inicio,
            args.n_fin,
            mostrar_soluciones=args.mostrar_soluciones,
            mostrar_tablero=args.mostrar_tablero,
            limite_impresion=args.limite_impresion,
        )
        return

    solver = NReinas(args.n, seed=args.seed)

    if args.metodo == "backtracking":
        t0 = time.perf_counter()
        solver.resolver()
        t1 = time.perf_counter()
        print(f"n={args.n}: {solver.cantidad_soluciones()} soluciones en {t1 - t0:.4f}s")
        if args.mostrar_soluciones:
            # Si limite_impresion <= 0, mostrar todas las soluciones
            if args.limite_impresion is not None and args.limite_impresion > 0:
                to_show = solver.soluciones[: args.limite_impresion]
            else:
                to_show = solver.soluciones
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