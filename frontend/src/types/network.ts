export type NetworkGraphView = 'all' | 'clusters' | 'repeat';

export type NetworkNodeType = 'accused' | 'incident' | 'location';

export type NetworkEdgeType = 'co_accused' | 'location_overlap' | 'temporal_proximity';

export interface NetworkGraphFilters {
  crime_type?: string | null;
  district?: string | null;
  date_from?: string | null;
  date_to?: string | null;
  view?: NetworkGraphView;
}

export interface NetworkGraphNode {
  id: string;
  label: string;
  type: NetworkNodeType;
  accused_id?: number | null;
  age?: number | null;
  gender?: string | null;
  fir_count: number;
  is_absconding: boolean;
  risk_score: number;
  gang_cluster?: number | null;
  primary_district?: string | null;
  last_seen_date?: string | null;
  aliases: string[];
  size: number;
  color: string;
  centrality_score: number;
}

export interface EdgeIncident {
  case_master_id: number;
  crime_no?: string | null;
}

export interface NetworkGraphEdge {
  source: string;
  target: string;
  type: NetworkEdgeType;
  strength: number;
  incidents: EdgeIncident[];
  thickness: number;
  color: string;
}

export interface NetworkDensestNode {
  id?: string | null;
  name?: string | null;
  centrality_score: number;
}

export interface NetworkGraphMetadata {
  total_nodes: number;
  total_edges: number;
  largest_cluster_size: number;
  num_clusters: number;
  repeat_offender_count: number;
  densest_node?: NetworkDensestNode | null;
  generated_at: string;
}

export interface NetworkGraphResponse {
  nodes: NetworkGraphNode[];
  edges: NetworkGraphEdge[];
  metadata: NetworkGraphMetadata;
}

export interface AccusedFirSummary {
  case_master_id: number;
  crime_no?: string | null;
  crime_type?: string | null;
  date?: string | null;
  district?: string | null;
  status?: string | null;
}

export interface CoAccusedSummary {
  accused_id?: number | null;
  name: string;
  times_together: number;
  risk_score: number;
}

export interface CrimeTypeSummary {
  name: string;
  count: number;
}

export interface AccusedProfileResponse {
  accused_id?: number | null;
  row_id?: number | null;
  name: string;
  age?: number | null;
  gender?: string | null;
  fir_count: number;
  firs: AccusedFirSummary[];
  co_accused: CoAccusedSummary[];
  crime_types: CrimeTypeSummary[];
  modus_operandi?: string | null;
  risk_score: number;
  gang_cluster?: number | null;
  is_absconding: boolean;
  last_seen_date?: string | null;
  aliases: string[];
}

export interface NetworkSearchResult {
  accused_id?: number | null;
  row_id?: number | null;
  name: string;
  fir_count: number;
  risk_score: number;
  last_fir_date?: string | null;
}

export interface NetworkSearchResponse {
  results: NetworkSearchResult[];
}
