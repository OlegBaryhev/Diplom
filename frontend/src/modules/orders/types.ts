export enum OrderStatus {
  Pending = 'Pending',
  Processing = 'Processing',
  Shipped = 'Shipped',
  Delivered = 'Delivered',
  Cancelled = 'Cancelled',
}

export interface OrderItemCreate {
  product_id: number;
  quantity: number;
}

export interface OrderCreate {
  items: OrderItemCreate[];
}

export interface OrderItemRead {
  product_id: number;
  quantity: number;
}

export interface OrderRead {
  id: number;
  user_id: number;
  status: OrderStatus;
  created_at: string;
  pickup_code: string;
  items: OrderItemRead[];
}
