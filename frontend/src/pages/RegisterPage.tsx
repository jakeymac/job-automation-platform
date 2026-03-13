export default function RegisterPage() {
  return (
    <div>
      <h2>Register</h2>

      <form style={{ display: "flex", flexDirection: "column", gap: "10px", maxWidth: "300px" }}>
          <input placeholder="Username" />
          <input placeholder="Email" />
          <input type="password" placeholder="Password" />

          <button>Register</button>
      </form>
    </div>
  )
}