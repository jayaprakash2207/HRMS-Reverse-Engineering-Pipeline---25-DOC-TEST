import React from 'react';
import { Link } from 'react-router-dom';

export function NotFoundPage(): JSX.Element {
  return (
    <main>
      <h1>Page not found</h1>
      <p>
        <Link to="/">Return home</Link>
      </p>
    </main>
  );
}
