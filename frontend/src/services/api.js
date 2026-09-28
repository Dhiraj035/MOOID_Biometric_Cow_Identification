const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";
export function getToken() {
  return localStorage.getItem("moo_id_token");
}

export function saveToken(token) {
  localStorage.setItem("moo_id_token", token);
}

export function removeToken() {
  localStorage.removeItem("moo_id_token");
}

// ===============================
// REGISTER USER
// ===============================

export async function registerUser(userData) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Registration failed."
    );
  }

  return data;
}


// ===============================
// LOGIN
// ===============================

export async function loginUser(email, password) {
  const formData = new URLSearchParams();

  formData.append("username", email);
  formData.append("password", password);

  const response = await fetch(
    `${API_BASE_URL}/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Login failed."
    );
  }

  saveToken(data.access_token);

  return data;
}


// ===============================
// CURRENT USER
// ===============================

export async function getCurrentUser() {
  const token = getToken();

  if (!token) {
    throw new Error(
      "No authentication token found."
    );
  }

  const response = await fetch(
    `${API_BASE_URL}/auth/me`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    removeToken();

    throw new Error(
      data.detail || "Authentication failed."
    );
  }

  return data;
}


// ===============================
// LOGOUT
// ===============================

export function logoutUser() {
  removeToken();
}


// ===============================
// BACKEND HEALTH
// ===============================

export async function checkBackendHealth() {
  const response = await fetch(
    `${API_BASE_URL}/health`
  );

  if (!response.ok) {
    throw new Error(
      "Moo-ID backend is not available."
    );
  }

  return await response.json();
}


// ===============================
// IDENTIFY COW
// ===============================

export async function identifyCow(imageFile) {
  const formData = new FormData();

  formData.append("file", imageFile);

  const token = getToken();

  const response = await fetch(
    `${API_BASE_URL}/identify`,
    {
      method: "POST",
      headers: token
        ? {
            Authorization: `Bearer ${token}`,
          }
        : {},
      body: formData,
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "Backend returned an invalid response."
    );
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
      `Identification failed: ${response.status}`
    );
  }

  return data;
}


// ===============================
// DASHBOARD STATS
// ===============================

export async function getDashboardStats() {
  const token = getToken();

  if (!token) {
    throw new Error(
      "You are not logged in."
    );
  }

  const response = await fetch(
    `${API_BASE_URL}/dashboard/stats`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to load dashboard statistics."
    );
  }

  return data;
}


// ===============================
// REGISTER COW
// ===============================
export async function registerCow(cowData) {
  const token = getToken();

  if (!token) {
    throw new Error("You are not logged in.");
  }

  const formData = new FormData();

  formData.append(
    "cow_id",
    cowData.cow_id
  );

  formData.append(
    "cow_name",
    cowData.cow_name
  );

  formData.append(
    "owner_name",
    cowData.owner_name
  );

  formData.append(
    "owner_phone",
    cowData.owner_phone
  );

  formData.append(
    "owner_address",
    cowData.owner_address
  );

  formData.append(
    "file",
    cowData.file
  );

  const response = await fetch(
    `${API_BASE_URL}/cows/register`,
    {
      method: "POST",

      headers: {
        Authorization: `Bearer ${token}`,
      },

      body: formData,
    }
  );

  let data;

  try {

    data = await response.json();

  } catch {

    throw new Error(
      "Backend returned an invalid response."
    );
  }

  if (!response.ok) {

    let message =
      "Failed to register cow.";

    if (
      typeof data.detail ===
      "string"
    ) {

      message = data.detail;

    } else if (
      Array.isArray(data.detail)
    ) {

      message = data.detail
        .map(
          (item) =>
            item.msg ||
            "Invalid input."
        )
        .join(", ");
    }

    throw new Error(
      message
    );
  }

  return data;
}

export async function getMyCows() {
  const token = getToken();

  if (!token) {
    throw new Error(
      "You are not logged in."
    );
  }

  const response = await fetch(
    `${API_BASE_URL}/cows/my-cows`,
    {
      method: "GET",

      headers: {
        Authorization:
          `Bearer ${token}`,
      },
    }
  );

  const data =
    await response.json();

if (!response.ok) {
  console.error("Dashboard API status:", response.status);
  console.error("Dashboard API response:", data);

  let message = "Failed to load dashboard statistics.";

  if (typeof data.detail === "string") {
    message = data.detail;
  } else if (Array.isArray(data.detail)) {
    message = data.detail
      .map((item) => item.msg || JSON.stringify(item))
      .join(", ");
  } else if (data.detail) {
    message = JSON.stringify(data.detail);
  }

  throw new Error(message);
}

  return data;
}