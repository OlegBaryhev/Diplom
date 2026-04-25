export interface CartItem {
  id: number;
  user_id: number;
  product_id: number;
  quantity: number;
}

export interface CartItemCreate {
  product_id: number;
  quantity: number;
}

export interface CartSearchItem {
  id: number;
  user: any;
  products_total: number;
  total_price: number;
}
