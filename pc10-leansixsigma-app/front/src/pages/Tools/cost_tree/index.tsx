import React, { useState, useEffect } from 'react';
import { Plus, Trash2, ChevronRight, ChevronDown, DollarSign, TreeDeciduous } from 'lucide-react';

// Categorías basadas en Lean Six Sigma y Lean Accounting
const CATEGORIAS: string[] = [
  'prevencion',
  'evaluacion',
  'falla_interna',
  'falla_externa'
];

interface CostNodeData {
  id: string;
  category: string;
  description: string;
  amount: number;
  total?: number;
  children: CostNodeData[];
}

interface CostNodeProps {
  node: CostNodeData;
  onUpdate: (id: string, newData: CostNodeData) => void;
  onDelete: (id: string) => void;
  onAddChild: (parentId: string) => void;
  level?: number;
}

// Componente Recursivo para cada Nodo del Árbol
const CostNode: React.FC<CostNodeProps> = ({ node, onUpdate, onDelete, onAddChild, level = 0 }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  // Determinar si es un nodo hoja (sin hijos) o una rama
  const isLeaf = node.children.length === 0;

  // Calcular el total del nodo actual
  const nodeTotal = isLeaf
    ? node.amount
    : node.children.reduce((sum, child) => sum + (child.total || child.amount), 0);

  // Efecto para propagar el total hacia arriba cuando cambian los hijos
  useEffect(() => {
    if (!isLeaf && node.total !== nodeTotal) {
      onUpdate(node.id, { ...node, total: nodeTotal });
    }
  }, [nodeTotal, isLeaf, node, onUpdate]);

  return (
    <div
      style={{
        marginLeft: `${level * 20}px`,
        position: 'relative',
      }}
    >
      {/* Conector vertical para niveles hijos */}
      {level > 0 && (
        <div
          style={{
            position: 'absolute',
            left: `${(level - 1) * 20 + 9}px`,
            top: 0,
            bottom: 0,
            width: '1px',
            backgroundColor: '#e5e7eb',
          }}
        />
      )}

      {/* Fila del Nodo */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 8px',
          borderBottom: '1px solid #f3f4f6',
          backgroundColor: level === 0 ? '#eff6ff' : '#ffffff',
          fontWeight: level === 0 ? 600 : 400,
        }}
      >
        {/* Botón Expander */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          disabled={isLeaf}
          style={{
            border: 'none',
            background: 'transparent',
            padding: 4,
            cursor: isLeaf ? 'default' : 'pointer',
            color: isLeaf ? '#d1d5db' : '#6b7280',
          }}
        >
          {isLeaf ? (
            <div style={{ width: 16 }} />
          ) : isExpanded ? (
            <ChevronDown size={16} />
          ) : (
            <ChevronRight size={16} />
          )}
        </button>

        {/* Selección de Categoría */}
        <select
          value={node.category}
          onChange={(e) => onUpdate(node.id, { ...node, category: e.target.value })}
          style={{
            borderRadius: '4px',
            border: '1px solid #d1d5db',
            padding: '2px 6px',
            fontSize: '13px',
            backgroundColor: '#ffffff',
            outline: 'none',
            width: '160px',
          }}
        >
          {CATEGORIAS.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>

        {/* Input Descripción */}
        <input
          type="text"
          value={node.description}
          onChange={(e) => onUpdate(node.id, { ...node, description: e.target.value })}
          placeholder="Descripción del gasto..."
          style={{
            flex: 1,
            borderRadius: '4px',
            border: '1px solid #d1d5db',
            padding: '2px 6px',
            fontSize: '13px',
            outline: 'none',
          }}
        />

        {/* Input Monto (Bloqueado si tiene hijos, editable si es hoja) */}
        <div style={{ position: 'relative', width: '120px' }}>
          <span
            style={{
              position: 'absolute',
              left: 6,
              top: 3,
              fontSize: '12px',
              color: '#6b7280',
            }}
          >
            $
          </span>
          <input
            type="number"
            value={isLeaf ? node.amount : nodeTotal}
            onChange={(e) =>
              isLeaf &&
              onUpdate(node.id, { ...node, amount: parseFloat(e.target.value || '0') || 0 })
            }
            readOnly={!isLeaf}
            style={{
              width: '100%',
              borderRadius: '4px',
              border: '1px solid #d1d5db',
              padding: '2px 6px 2px 16px',
              fontSize: '13px',
              textAlign: 'right',
              outline: 'none',
              backgroundColor: !isLeaf ? '#f9fafb' : '#ffffff',
              fontWeight: !isLeaf ? 600 : 400,
              color: !isLeaf ? '#374151' : '#111827',
            }}
          />
        </div>

        {/* Botones de Acción */}
        <div style={{ display: 'flex', gap: '4px' }}>
          <button
            onClick={() => onAddChild(node.id)}
            title="Agregar Sub-costo"
            style={{
              border: 'none',
              padding: 4,
              borderRadius: '4px',
              backgroundColor: '#ecfdf3',
              color: '#16a34a',
              cursor: 'pointer',
            }}
          >
            <Plus size={16} />
          </button>
          {level > 0 && (
            <button
              onClick={() => onDelete(node.id)}
              title="Eliminar línea"
              style={{
                border: 'none',
                padding: 4,
                borderRadius: '4px',
                backgroundColor: '#fef2f2',
                color: '#dc2626',
                cursor: 'pointer',
              }}
            >
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Renderizado Recursivo de Hijos */}
      {isExpanded &&
        node.children.map((child) => (
          <CostNode
            key={child.id}
            node={child}
            level={level + 1}
            onUpdate={onUpdate}
            onDelete={onDelete}
            onAddChild={onAddChild}
          />
        ))}
    </div>
  );
};

// Componente Principal
const CostTreeApp: React.FC = () => {
  // Estado Inicial: Nodo Raíz del Costo Total
  const [data, setData] = useState<CostNodeData[]>([
    {
      id: 'root',
      category: 'General',
      description: 'Costo Total del Proyecto / Proceso',
      amount: 0,
      total: 0,
      children: [],
    },
  ]);

  const [income, setIncome] = useState<number>(0);

  // Funciones auxiliares para manipular el árbol
  const updateNodeRecursive = (nodes: CostNodeData[], id: string, newData: CostNodeData): CostNodeData[] => {
    return nodes.map((node) => {
      if (node.id === id) return { ...newData, children: node.children };
      return { ...node, children: updateNodeRecursive(node.children, id, newData) };
    });
  };

  const addNodeRecursive = (nodes: CostNodeData[], parentId: string): CostNodeData[] => {
    return nodes.map((node) => {
      if (node.id === parentId) {
        return {
          ...node,
          children: [
            ...node.children,
            {
              id: Math.random().toString(36).substr(2, 9),
              category: 'Materiales',
              description: '',
              amount: 0,
              children: [],
            },
          ],
        };
      }
      return { ...node, children: addNodeRecursive(node.children, parentId) };
    });
  };

  const deleteNodeRecursive = (nodes: CostNodeData[], id: string): CostNodeData[] => {
    return nodes
      .filter((node) => node.id !== id)
      .map((node) => ({ ...node, children: deleteNodeRecursive(node.children, id) }));
  };

  // Handlers
  const handleUpdate = (id: string, newData: CostNodeData) => setData((prev) => updateNodeRecursive(prev, id, newData));
  const handleAddChild = (parentId: string) => setData((prev) => addNodeRecursive(prev, parentId));
  const handleDelete = (id: string) => setData((prev) => deleteNodeRecursive(prev, id));

  // Cálculos de Resumen
  const totalCost =
    data[0].children.length > 0
      ? data[0].children.reduce((acc, child) => acc + (child.total || child.amount), 0)
      : data[0].amount;

  const profit = income - totalCost;
  const margin = income > 0 ? ((profit / income) * 100).toFixed(2) : 0;

  return (
    <div
      style={{
        maxWidth: '960px',
        margin: '40px auto',
        padding: '24px',
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '24px',
          paddingBottom: '16px',
          borderBottom: '1px solid #e5e7eb',
        }}
      >
        <TreeDeciduous color="#16a34a" size={32} />
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#111827', margin: 0 }}>
            Árbol de Costos (Cost Tree)
          </h1>
          <p style={{ fontSize: '13px', color: '#6b7280', marginTop: '4px' }}>
            Basado en metodología Lean Accounting y Análisis de Valor
          </p>
        </div>
      </div>

      {/* Dashboard de Resumen Financiero */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '16px',
          marginBottom: '24px',
        }}
      >
        {/* Card Ingresos */}
        <div
          style={{
            backgroundColor: '#ecfdf3',
            padding: '16px',
            borderRadius: '8px',
            border: '1px solid #bbf7d0',
          }}
        >
          <label
            style={{
              display: 'block',
              fontSize: '13px',
              fontWeight: 600,
              color: '#166534',
              marginBottom: '4px',
            }}
          >
            Ingresos Totales
          </label>
          <div style={{ position: 'relative' }}>
            <DollarSign
              style={{ position: 'absolute', left: 8, top: 8 }}
              color="#16a34a"
              size={18}
            />
            <input
              type="number"
              value={income}
              onChange={(e) => setIncome(parseFloat(e.target.value || '0') || 0)}
              style={{
                width: '100%',
                padding: '6px 12px 6px 30px',
                borderRadius: '6px',
                border: '1px solid #86efac',
                outline: 'none',
              }}
            />
          </div>
        </div>

        {/* Card Costos */}
        <div
          style={{
            backgroundColor: '#fef2f2',
            padding: '16px',
            borderRadius: '8px',
            border: '1px solid #fecaca',
          }}
        >
          <label
            style={{
              display: 'block',
              fontSize: '13px',
              fontWeight: 600,
              color: '#b91c1c',
              marginBottom: '4px',
            }}
          >
            Costos Totales (Calculado)
          </label>
          <div
            style={{
              fontSize: '22px',
              fontWeight: 700,
              color: '#b91c1c',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <DollarSign size={20} />
            {totalCost.toLocaleString('es-PE', { minimumFractionDigits: 2 })}
          </div>
        </div>

        {/* Card Rentabilidad */}
        <div
          style={{
            padding: '16px',
            borderRadius: '8px',
            border: `1px solid ${profit >= 0 ? '#bfdbfe' : '#fed7aa'}`,
            backgroundColor: profit >= 0 ? '#eff6ff' : '#fff7ed',
          }}
        >
          <label
            style={{
              display: 'block',
              fontSize: '13px',
              fontWeight: 600,
              color: '#374151',
              marginBottom: '4px',
            }}
          >
            Utilidad Neta / Margen
          </label>
          <div
            style={{
              fontSize: '22px',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: profit >= 0 ? '#1d4ed8' : '#c2410c',
            }}
          >
            <span>
              $ {profit.toLocaleString('es-PE', { minimumFractionDigits: 2 })}
            </span>
            <span
              style={{
                fontSize: '12px',
                padding: '2px 8px',
                borderRadius: '999px',
                backgroundColor: 'rgba(255,255,255,0.7)',
                border: '1px solid #e5e7eb',
              }}
            >
              {margin}%
            </span>
          </div>
        </div>
      </div>

      {/* Árbol de Costos */}
      <div
        style={{
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
          overflow: 'hidden',
          backgroundColor: '#ffffff',
        }}
      >
        <div
          style={{
            backgroundColor: '#f3f4f6',
            padding: '8px',
            display: 'flex',
            fontSize: '11px',
            fontWeight: 700,
            color: '#6b7280',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            borderBottom: '1px solid #e5e7eb',
          }}
        >
          <div style={{ width: '32px' }} /> {/* Espacio flecha */}
          <div style={{ width: '190px', paddingLeft: '8px' }}>Categoría</div>
          <div style={{ flex: 1, paddingLeft: '8px' }}>Descripción del Item</div>
          <div style={{ width: '130px', textAlign: 'right', paddingRight: '8px' }}>Monto</div>
          <div style={{ width: '80px', textAlign: 'center' }}>Acción</div>
        </div>

        <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
          {data.map((node) => (
            <CostNode
              key={node.id}
              node={node}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
              onAddChild={handleAddChild}
            />
          ))}
        </div>
      </div>

      <div
        style={{
          marginTop: '12px',
          fontSize: '11px',
          color: '#9ca3af',
          fontStyle: 'italic',
        }}
      >
        * Nota: Los montos de las categorías padres se calculan automáticamente sumando sus
        sub-elementos (Roll-up).
      </div>
    </div>
  );
};

export default CostTreeApp;
