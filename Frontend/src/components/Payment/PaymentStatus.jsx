import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";

const PaymentStatus = () => {
  const [status, setStatus] = useState("Checking payment status...");
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const orderId = params.get("order_id");

  useEffect(() => {
    if (orderId) {
      axios
        .get(`http://localhost:5000/payment-status?order_id=${orderId}`)
        .then((response) => {
          if (response.data.order_status === "PAID") {
            setStatus("✅ Payment Successful!");
          } else {
            setStatus("❌ Payment Failed or Pending.");
          }
        })
        .catch(() => {
          setStatus("⚠️ Error fetching payment status.");
        });
    }
  }, [orderId]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white shadow-lg rounded-lg p-6 text-center">
        <h2 className="text-2xl font-bold">{status}</h2>
        <p className="text-gray-500 mt-2">Order ID: {orderId}</p>
      </div>
    </div>
  );
};

export default PaymentStatus;
