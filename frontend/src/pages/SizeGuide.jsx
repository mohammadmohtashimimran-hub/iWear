import { Link } from 'react-router-dom'

const SIZES = [
  { size: 'Narrow',      width: '130 – 133 mm', face: 'Thin Face',   apparel: 'S' },
  { size: 'Medium',      width: '134 – 137 mm', face: 'Normal Face', apparel: 'M' },
  { size: 'Wide',        width: '138 – 141 mm', face: 'Healthy Face',apparel: 'L' },
  { size: 'Extra Wide',  width: '142 & above',  face: 'Big Face',    apparel: 'XL' },
]

export default function SizeGuide() {
  return (
    <div className="sg-page">
      {/* Hero */}
      <section className="sg-hero">
        <h1>Eyewear Size Guide</h1>
        <p>Find the perfect fit. Follow our simple guide to measure your frame size at home.</p>
      </section>

      {/* Section 1 — How to measure */}
      <section className="sg-section">
        <div className="sg-two-col">
          <div className="sg-img-wrap">
            <img src="/uploads/sizeguides/size-guide1.jpeg" alt="How to measure your frame size" />
          </div>
          <div className="sg-text">
            <h2>How to Measure Your Frame Size</h2>
            <ol className="sg-steps">
              <li>
                <strong>Step 1</strong>
                <span>Stand straight in front of a mirror with a ruler.</span>
              </li>
              <li>
                <strong>Step 2</strong>
                <span>Hold the ruler horizontally across your face, slightly below your eye level. Ensure the ruler is straight.</span>
              </li>
              <li>
                <strong>Step 3</strong>
                <span>Measure the distance between your temples (the widest point of your face).</span>
              </li>
              <li>
                <strong>Step 4</strong>
                <span>Make a note of your measurement in millimetres and match it to the size chart below.</span>
              </li>
            </ol>
          </div>
        </div>
      </section>

      {/* Section 2 — Find by apparel */}
      <section className="sg-section sg-section-alt">
        <div className="sg-two-col sg-two-col-reverse">
          <div className="sg-img-wrap">
            <img src="/uploads/sizeguides/size-guide2.jpeg" alt="Find your glasses size with apparel size" />
          </div>
          <div className="sg-text">
            <h2>Don't Have a Ruler?</h2>
            <p>No worries! You can also find your eyewear size using your clothing (apparel) size as a quick reference.</p>
            <div className="sg-apparel-grid">
              {SIZES.map(s => (
                <div key={s.apparel} className="sg-apparel-card">
                  <span className="sg-apparel-letter">{s.apparel}</span>
                  <span className="sg-apparel-label">{s.size}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Section 3 — Size chart table */}
      <section className="sg-section">
        <div className="sg-center">
          <h2>Size Chart</h2>
          <p className="sg-subtitle">Match your temple-to-temple measurement to find your perfect frame size.</p>
          <div className="sg-table-wrap">
            <table className="sg-table">
              <thead>
                <tr>
                  <th>Size</th>
                  <th>Glasses Width</th>
                  <th>Face Type</th>
                  <th>Apparel</th>
                </tr>
              </thead>
              <tbody>
                {SIZES.map(s => (
                  <tr key={s.size}>
                    <td><strong>{s.size}</strong></td>
                    <td>{s.width}</td>
                    <td>{s.face}</td>
                    <td><span className="sg-tag">{s.apparel}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="sg-note">
            <strong>Note:</strong> 80% of people fit in Medium &amp; Wide size.
          </div>
        </div>
      </section>

      {/* Section 4 — Reference image */}
      <section className="sg-section sg-section-alt">
        <div className="sg-center">
          <h2>Visual Reference</h2>
          <p className="sg-subtitle">Here's a quick look at how different sizes compare.</p>
          <div className="sg-img-wrap sg-img-full">
            <img src="/uploads/sizeguides/size-guide3.jpeg" alt="Size chart reference" />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="sg-cta">
        <h2>Ready to find your perfect pair?</h2>
        <Link to="/" className="btn btn-primary" style={{ padding: '0.75rem 2.5rem', fontSize: '1.05rem' }}>
          Shop Now
        </Link>
      </section>
    </div>
  )
}
