/**
 * Makazi — Client API pour communiquer avec le backend FastAPI.
 *
 * CORRECTION BUG 3 : Ajout des slashes finaux sur toutes les URLs.
 * Sans le slash final, FastAPI renvoie un 307 Redirect vers l'URL avec slash.
 * Sur un POST, fetch() ne suit pas correctement ce redirect → 404 ou échec silencieux.
 */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApartmentData {
  type_quartier: "Administratif" | "Résidentiel" | "Populaire";
  chambres: number;
  douches: number;
  salons: number;
  cuisines: number;
  bureaux: number;
  forage: boolean;
  eneo: boolean;
  loyer: number;
}

export interface PredictionRequest {
  type_quartier: "Administratif" | "Résidentiel" | "Populaire";
  chambres: number;
  douches: number;
  salons: number;
  cuisines: number;
  bureaux: number;
  forage: boolean;
  eneo: boolean;
}

export interface PredictionResponse {
  predicted_price: number;
  lower_bound: number;
  upper_bound: number;
}

export interface StatsResponse {
  total_entries: number;
  average_price: number;
  r_squared: number | null;
}

export interface DistributionItem {
  type_quartier: string;
  count: number;
  min: number;
  max: number;
  average: number;
  loyers: number[];
}

export async function collectData(data: ApartmentData) {
  const res = await fetch(`${API_BASE}/collect/`, {   // slash final ajouté
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    if (res.status === 422) {
      throw new Error(
        "Erreur : Le loyer renseigné ne semble pas cohérent avec le type de quartier et/ou ce bien."
      );
    }
    throw new Error("Erreur serveur : Impossible d'enregistrer les données.");
  }

  return res.json();
}

export async function getStats(): Promise<StatsResponse> {
  const res = await fetch(`${API_BASE}/stats/`);      // slash final ajouté
  if (!res.ok) throw new Error("Erreur lors du chargement des statistiques");
  return res.json();
}

export async function predict(data: PredictionRequest): Promise<PredictionResponse> {
  const res = await fetch(`${API_BASE}/predict/`, {   // slash final ajouté
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Erreur lors de la prédiction");
  return res.json();
}

export async function getDistribution(): Promise<DistributionItem[]> {
  const res = await fetch(`${API_BASE}/distribution/`); // slash final ajouté
  if (!res.ok) throw new Error("Erreur lors du chargement de la distribution");
  return res.json();
}
