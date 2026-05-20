export interface Plant {
  id: string;
  name: string;
  species: string;
  photos: string[];
  frequency: {
    water: number;    // days
    fertilizer: number; // days
    transplant: number; // days
  };
  status: 'healthy' | 'treatment' | 'archived';
  created_at: string;
}

export interface Task {
  id: string;
  plant_id: string;
  plant_name: string;
  type: 'water' | 'fertilize' | 'transplant' | 'review';
  due_date: string;
  completed: boolean;
}

export interface Diagnosis {
  id: string;
  plant_id?: string;
  photo: string;
  diseases: Array<{
    name: string;
    probability: number;
    treatment: string;
  }>;
  created_at: string;
}
