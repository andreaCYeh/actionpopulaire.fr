import { useCallback, useEffect, useRef, useState } from "react";
import throttle from "lodash/throttle";
import debounce from "lodash/debounce";
import { disableBodyScroll, clearAllBodyScrollLocks } from "body-scroll-lock";

export const usePrevious = (value) => {
  const ref = useRef(null);
  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
};

/**
 * Crée une version throttled de la fonction limite
 * Même si la fonction change, le throttling reste appliqué de
 * la même façon.
 *
 * Attention : changer la limite resette le throttling.
 *
 * @param {Function} func la fonction à throttler
 * @param {number} wait le nombre de millisecondes pour lesquelles throttler la fonction
 */
export const useThrottle = (func, wait) => {
  const ref = useRef(null);
  ref.current = func;

  /* exhaustive-deps n'arrive pas à identifier automatiquement les dépendances
     à cause de l'utilisation de la fonction externe throttle. On pourrait utiliser
     useMemo à la place mais l'objectif poursuivi serait moins clair. */

  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useCallback(
    throttle((...args) => ref.current(...args), wait, {
      leading: true,
      trailing: true,
    }),
    [wait]
  );
};

/**
 * Crée une version debounced de la fonction limite
 * Même si la fonction change, le debounced reste appliqué de
 * la même façon.
 *
 * Attention : changer la limite resette le debounce.
 *
 * @param {Function} func la fonction à debouncer
 * @param {number} wait le nombre de millisecondes pour lesquelles debouncer la fonction
 * @param {Array} deps éventuels paramètres supplémentaires dont le changement déclenche le "reset" du debounce.
 */
export const useDebounce = (func, wait, deps = []) => {
  const ref = useRef(null);
  ref.current = func;

  /* L'utilisation d'une fonction arrow pour appeler ref.current, plutôt
  que d'utiliser ref.current directe est délibérée ! Elle permet de s'assurer
  que c'est la valeur actuelle de la référence qui est utilisée à chaque fois
  que la fonction debounce s'active, alors qu'en indiquant directement ref.current,
  ç'aurait été la version au moment de la production du callback qui aurait été
  utilisée.

  exhaustive-deps n'arrive pas à identifier les dépendances et est désactivé ici. */
  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useCallback(
    debounce((...args) => ref.current(...args), wait, {
      leading: false,
      trailing: true,
    }),
    [wait, ...deps]
  );
};

/**
 * Permet de mettre en place l'exécution d'un callback tous les `delay` secondes
 *
 * @param {Function} callback le callback à appeler régulièrement
 * @param {number} delay le nombre de millisecondes d'attente entre deux invocation du callback
 *
 * En cas de changement du delay, l'intervalle actuel est supprimé et un nouvel intervalle est créé.
 * Par exemple, si on était à 10 ms de la prochaine exécution, même si on réduit la longueur de l'intervalle
 * de 1000 à 500, la prochaine exécution aura lieu dans 500 ms (et non dans 10).
 */
export const useInterval = function useInterval(callback, delay) {
  const savedCallback = useRef();

  // Remember the latest callback.
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval.
  useEffect(() => {
    function tick() {
      savedCallback.current();
    }

    if (delay !== null) {
      let id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
};

export const useDisableBodyScroll = (isActive, shouldDisable) => {
  const targetRef = useRef(null);

  useEffect(() => {
    if (isActive && targetRef.current) {
      shouldDisable
        ? disableBodyScroll(targetRef.current)
        : clearAllBodyScrollLocks();
    }
    return () => {
      clearAllBodyScrollLocks();
    };
  }, [shouldDisable, isActive]);

  return targetRef;
};

export function useMeasure() {
  const ref = useRef();
  const [bounds, set] = useState({ left: 0, top: 0, width: 0, height: 0 });
  const [resizeObserver] = useState(
    () => new ResizeObserver(([entry]) => set(entry.contentRect))
  );
  useEffect(() => {
    if (ref.current) resizeObserver.observe(ref.current);
    return () => resizeObserver.disconnect();
  }, [resizeObserver]);
  return [{ ref }, bounds];
}
