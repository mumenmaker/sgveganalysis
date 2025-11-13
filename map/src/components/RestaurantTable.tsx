import React, { useState, useMemo, useEffect, useCallback } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type ColumnResizeMode,
} from '@tanstack/react-table';
import type { Restaurant } from '../types/restaurant';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ExternalLink, ChevronLeft, ChevronRight, Check, Loader2 } from 'lucide-react';
import { updateRestaurant } from '../lib/supabase';

interface RestaurantTableProps {
  restaurants: Restaurant[];
  isDarkMode?: boolean;
  selectedRestaurantId?: number | null;
  onRestaurantSelect?: (restaurantId: number | null) => void;
  onRestaurantUpdate?: (updatedRestaurant: Restaurant) => void;
}

const RestaurantTable: React.FC<RestaurantTableProps> = ({ 
  restaurants, 
  isDarkMode = false, 
  selectedRestaurantId, 
  onRestaurantSelect,
  onRestaurantUpdate 
}) => {
  const [columnResizeMode] = useState<ColumnResizeMode>('onChange');
  const [editingData, setEditingData] = useState<Map<number, Partial<Restaurant>>>(new Map());
  const [updatingIds, setUpdatingIds] = useState<Set<number>>(new Set());

  // Initialize editing data when row is selected
  useEffect(() => {
    if (selectedRestaurantId) {
      const restaurant = restaurants.find(r => r.id === selectedRestaurantId);
      if (restaurant && !editingData.has(selectedRestaurantId)) {
        setEditingData(prev => {
          const newMap = new Map(prev);
          newMap.set(selectedRestaurantId, { ...restaurant });
          return newMap;
        });
      }
    } else {
      // Clear editing data when no row is selected
      setEditingData(new Map());
    }
  }, [selectedRestaurantId, restaurants]);

  // Handle field updates
  const handleFieldChange = (restaurantId: number, field: keyof Restaurant, value: any) => {
    setEditingData(prev => {
      const newMap = new Map(prev);
      const current = newMap.get(restaurantId) || {};
      newMap.set(restaurantId, { ...current, [field]: value });
      return newMap;
    });
  };

  // Handle submit
  const handleSubmit = useCallback(async (restaurantId: number) => {
    const updates = editingData.get(restaurantId);
    if (!updates) return;

    // Remove id and other non-updatable fields, and only include changed fields
    const { id, created_at, updated_at, scraped_at, ...updateFields } = updates;
    
    // Check if there are any actual changes
    const original = restaurants.find(r => r.id === restaurantId);
    if (!original) return;

    const hasChanges = Object.keys(updateFields).some(key => {
      const originalValue = original[key as keyof Restaurant];
      const newValue = updateFields[key as keyof typeof updateFields];
      return originalValue !== newValue;
    });

    if (!hasChanges) return;

    setUpdatingIds(prev => new Set(prev).add(restaurantId));
    try {
      const updated = await updateRestaurant(restaurantId, updateFields);
      if (onRestaurantUpdate) {
        onRestaurantUpdate(updated);
      }
      // Clear editing data for this row
      setEditingData(prev => {
        const newMap = new Map(prev);
        newMap.delete(restaurantId);
        return newMap;
      });
    } catch (error) {
      console.error('Failed to update restaurant:', error);
      alert('Failed to update restaurant. Please try again.');
    } finally {
      setUpdatingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(restaurantId);
        return newSet;
      });
    }
  }, [editingData, onRestaurantUpdate, restaurants]);

  // Helper to render editable cell
  const renderEditableCell = (
    restaurant: Restaurant,
    field: keyof Restaurant,
    value: any,
    type: 'text' | 'textarea' | 'number' = 'text',
    className: string = ''
  ) => {
    const isSelected = selectedRestaurantId === restaurant.id;
    const isEditing = isSelected && editingData.has(restaurant.id);
    const editedValue = isEditing ? (editingData.get(restaurant.id)?.[field] ?? value) : value;

    if (!isEditing) {
      return (
        <div className={className}>
          {value || '-'}
        </div>
      );
    }

    if (type === 'textarea') {
      return (
        <textarea
          value={editedValue || ''}
          onChange={(e) => handleFieldChange(restaurant.id, field, e.target.value)}
          className={`w-full px-2 py-1 text-sm border rounded ${isDarkMode ? 'bg-slate-700 border-slate-600 text-white' : 'bg-white border-gray-300'} ${className}`}
          rows={2}
        />
      );
    }

    if (type === 'number') {
      return (
        <input
          type="number"
          value={editedValue ?? ''}
          onChange={(e) => handleFieldChange(restaurant.id, field, e.target.value ? parseFloat(e.target.value) : null)}
          className={`w-full px-2 py-1 text-sm border rounded ${isDarkMode ? 'bg-slate-700 border-slate-600 text-white' : 'bg-white border-gray-300'} ${className}`}
          step="0.1"
        />
      );
    }

    return (
      <input
        type="text"
        value={editedValue || ''}
        onChange={(e) => handleFieldChange(restaurant.id, field, e.target.value)}
        className={`w-full px-2 py-1 text-sm border rounded ${isDarkMode ? 'bg-slate-700 border-slate-600 text-white' : 'bg-white border-gray-300'} ${className}`}
      />
    );
  };

  // Define columns
  const columns = useMemo<ColumnDef<Restaurant>[]>(
    () => [
      {
        accessorKey: 'name',
        header: 'Name',
        cell: (info) => {
          const restaurant = info.row.original;
          const value = info.getValue() as string;
          return renderEditableCell(restaurant, 'name', value, 'text', `font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`);
        },
        size: 200,
        minSize: 100,
        maxSize: 400,
      },
      {
        accessorKey: 'description',
        header: 'Description',
        cell: (info) => {
          const restaurant = info.row.original;
          const value = info.getValue() as string | undefined;
          return renderEditableCell(restaurant, 'description', value, 'textarea', `text-sm ${isDarkMode ? 'text-slate-300' : 'text-gray-600'}`);
        },
        size: 300,
        minSize: 150,
        maxSize: 600,
      },
      {
        accessorKey: 'address',
        header: 'Address',
        cell: (info) => {
          const restaurant = info.row.original;
          const value = info.getValue() as string | undefined;
          return renderEditableCell(restaurant, 'address', value, 'text', `text-sm ${isDarkMode ? 'text-slate-300' : 'text-gray-600'}`);
        },
        size: 250,
        minSize: 150,
        maxSize: 400,
      },
      {
        accessorKey: 'phone',
        header: 'Phone',
        cell: (info) => {
          const restaurant = info.row.original;
          const value = info.getValue() as string | undefined;
          return renderEditableCell(restaurant, 'phone', value, 'text', `text-sm ${isDarkMode ? 'text-slate-300' : 'text-gray-600'}`);
        },
        size: 150,
        minSize: 100,
        maxSize: 200,
      },
      {
        accessorKey: 'cow_reviews',
        header: 'HappyCow Reviews',
        cell: (info) => {
          const restaurant = info.row.original;
          const url = info.getValue() as string | undefined;
          const isSelected = selectedRestaurantId === restaurant.id;
          const isEditing = isSelected && editingData.has(restaurant.id);
          
          if (isEditing) {
            const editedValue = editingData.get(restaurant.id)?.cow_reviews ?? url;
            return (
              <input
                type="url"
                value={editedValue || ''}
                onChange={(e) => handleFieldChange(restaurant.id, 'cow_reviews', e.target.value)}
                className={`w-full px-2 py-1 text-sm border rounded ${isDarkMode ? 'bg-slate-700 border-slate-600 text-white' : 'bg-white border-gray-300'}`}
                placeholder="https://..."
              />
            );
          }
          
          return url ? (
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className={`inline-flex items-center space-x-1 p-1.5 rounded hover:${isDarkMode ? 'bg-slate-700' : 'bg-gray-100'} transition-colors`}
              title="View on HappyCow"
            >
              <ExternalLink className={`h-4 w-4 ${isDarkMode ? 'text-green-400' : 'text-green-600'}`} />
              <span className={`text-sm ${isDarkMode ? 'text-slate-300' : 'text-gray-600'}`}>View</span>
            </a>
          ) : (
            <span className={`${isDarkMode ? 'text-slate-400' : 'text-gray-400'} text-sm`}>-</span>
          );
        },
        size: 150,
        minSize: 120,
        maxSize: 200,
      },
      {
        accessorKey: 'category',
        header: 'Category',
        cell: (info) => {
          const restaurant = info.row.original;
          const value = info.getValue() as string | undefined;
          return renderEditableCell(restaurant, 'category', value, 'text', `text-sm ${isDarkMode ? 'text-slate-300' : 'text-gray-600'}`);
        },
        size: 150,
        minSize: 100,
        maxSize: 250,
      },
      {
        accessorKey: 'is_vegan',
        header: 'Vegan',
        cell: (info) => {
          const isVegan = info.getValue() as boolean;
          return isVegan ? (
            <Badge variant="default" className="bg-green-500 text-white border-green-600 text-xs">
              🌱 Yes
            </Badge>
          ) : (
            <span className={`${isDarkMode ? 'text-slate-400' : 'text-gray-400'} text-sm`}>No</span>
          );
        },
        size: 100,
        minSize: 80,
        maxSize: 120,
      },
      {
        accessorKey: 'is_vegetarian',
        header: 'Vegetarian',
        cell: (info) => {
          const isVegetarian = info.getValue() as boolean;
          return isVegetarian ? (
            <Badge variant="default" className="bg-orange-500 text-white border-orange-600 text-xs">
              🥗 Yes
            </Badge>
          ) : (
            <span className={`${isDarkMode ? 'text-slate-400' : 'text-gray-400'} text-sm`}>No</span>
          );
        },
        size: 120,
        minSize: 100,
        maxSize: 150,
      },
      {
        accessorKey: 'has_veg_options',
        header: 'Veg Options',
        cell: (info) => {
          const hasVegOptions = info.getValue() as boolean;
          return hasVegOptions ? (
            <Badge variant="outline" className="border-green-300 text-green-700 text-xs">
              🍃 Yes
            </Badge>
          ) : (
            <span className={`${isDarkMode ? 'text-slate-400' : 'text-gray-400'} text-sm`}>No</span>
          );
        },
        size: 120,
        minSize: 100,
        maxSize: 150,
      },
      {
        accessorKey: 'latitude',
        header: 'Latitude',
        cell: (info) => {
          const restaurant = info.row.original;
          const lat = info.getValue() as number | undefined;
          const displayValue = lat !== undefined && lat !== null ? lat : null;
          return renderEditableCell(restaurant, 'latitude', displayValue, 'number', `text-sm font-mono ${isDarkMode ? 'text-slate-300' : 'text-gray-600'}`);
        },
        size: 120,
        minSize: 100,
        maxSize: 150,
      },
      {
        accessorKey: 'longitude',
        header: 'Longitude',
        cell: (info) => {
          const restaurant = info.row.original;
          const lng = info.getValue() as number | undefined;
          const displayValue = lng !== undefined && lng !== null ? lng : null;
          return renderEditableCell(restaurant, 'longitude', displayValue, 'number', `text-sm font-mono ${isDarkMode ? 'text-slate-300' : 'text-gray-600'}`);
        },
        size: 120,
        minSize: 100,
        maxSize: 150,
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: (info) => {
          const restaurant = info.row.original;
          const isSelected = selectedRestaurantId === restaurant.id;
          const isUpdating = updatingIds.has(restaurant.id);
          const editedData = editingData.get(restaurant.id);
          const original = restaurants.find(r => r.id === restaurant.id);
          const hasChanges = editedData && original ? Object.keys(editedData).some(key => {
            if (key === 'id' || key === 'created_at' || key === 'updated_at' || key === 'scraped_at') return false;
            return original[key as keyof Restaurant] !== editedData[key as keyof typeof editedData];
          }) : false;

          if (!isSelected) {
            return <div className="px-2">-</div>;
          }

          return (
            <div className="flex items-center space-x-2">
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  handleSubmit(restaurant.id);
                }}
                disabled={isUpdating || !hasChanges}
                size="sm"
                className={`${isDarkMode ? 'bg-green-600 hover:bg-green-700' : 'bg-green-600 hover:bg-green-700'} text-white`}
              >
                {isUpdating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                    Updating...
                  </>
                ) : (
                  <>
                    <Check className="h-4 w-4 mr-1" />
                    Submit
                  </>
                )}
              </Button>
            </div>
          );
        },
        size: 120,
        minSize: 100,
        maxSize: 150,
      },
    ],
    [isDarkMode, selectedRestaurantId, editingData, updatingIds, handleSubmit]
  );

  const table = useReactTable({
    data: restaurants,
    columns,
    columnResizeMode,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 15,
      },
    },
  });

  if (restaurants.length === 0) {
    return (
      <div className={`p-8 text-center ${isDarkMode ? 'text-slate-300' : 'text-gray-600'}`}>
        <p>No restaurants found matching the current filters.</p>
      </div>
    );
  }

  return (
    <div className={`w-full h-full flex flex-col ${isDarkMode ? 'bg-slate-800/50' : 'bg-white/50'} backdrop-blur-sm`}>
      <div className="flex-1 overflow-auto">
        <div className="inline-block min-w-full align-middle">
          <table
            className="w-full border-collapse"
            style={{
              width: table.getCenterTotalSize(),
            }}
          >
            <thead className="sticky top-0 z-10">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr
                  key={headerGroup.id}
                  className={`border-b ${isDarkMode ? 'border-slate-700' : 'border-gray-200'}`}
                >
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      className={`relative px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider ${
                        isDarkMode ? 'text-slate-300 bg-slate-800/95' : 'text-gray-700 bg-white/95'
                      }`}
                      style={{
                        width: header.getSize(),
                      }}
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(header.column.columnDef.header, header.getContext())}
                      <div
                        onMouseDown={header.getResizeHandler()}
                        onTouchStart={header.getResizeHandler()}
                        className={`absolute right-0 top-0 h-full w-1 cursor-col-resize select-none touch-none ${
                          isDarkMode ? 'hover:bg-green-400' : 'hover:bg-green-600'
                        } ${
                          header.column.getIsResizing()
                            ? isDarkMode
                              ? 'bg-green-400'
                              : 'bg-green-600'
                            : ''
                        }`}
                        style={{
                          userSelect: 'none',
                          touchAction: 'none',
                        }}
                      />
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody className={`divide-y ${isDarkMode ? 'divide-slate-700' : 'divide-gray-200'} bg-transparent`}>
              {table.getRowModel().rows.map((row) => {
                const restaurant = row.original;
                const isSelected = selectedRestaurantId === restaurant.id;
                return (
                <tr
                  key={row.id}
                  onClick={() => onRestaurantSelect?.(restaurant.id)}
                  className={`cursor-pointer transition-colors duration-150 ${
                    isSelected
                      ? isDarkMode
                        ? 'bg-green-600/30 border-l-4 border-green-400'
                        : 'bg-green-100 border-l-4 border-green-600'
                      : `hover:${isDarkMode ? 'bg-slate-700/30' : 'bg-gray-50'}`
                  }`}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td
                      key={cell.id}
                      className={`px-4 py-3 ${isDarkMode ? 'text-slate-300' : 'text-gray-600'}`}
                      style={{
                        width: cell.column.getSize(),
                      }}
                    >
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {table.getPageCount() > 1 && (
        <div
          className={`px-4 py-3 border-t flex items-center justify-between ${
            isDarkMode ? 'border-slate-700' : 'border-gray-200'
          }`}
        >
          <div className={`text-sm ${isDarkMode ? 'text-slate-300' : 'text-gray-600'}`}>
            Showing {table.getState().pagination.pageIndex * 15 + 1} to{' '}
            {Math.min((table.getState().pagination.pageIndex + 1) * 15, restaurants.length)} of{' '}
            {restaurants.length} restaurants
          </div>
          <div className="flex items-center space-x-2">
            <Button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              variant="outline"
              size="sm"
              className={isDarkMode ? 'border-slate-600 text-slate-300 hover:bg-slate-700' : ''}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>

            <div className="flex items-center space-x-1">
              {Array.from({ length: Math.min(5, table.getPageCount()) }, (_, i) => {
                let pageNum: number;
                const totalPages = table.getPageCount();
                const currentPage = table.getState().pagination.pageIndex + 1;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }

                return (
                  <Button
                    key={pageNum}
                    onClick={() => table.setPageIndex(pageNum - 1)}
                    variant={currentPage === pageNum ? 'default' : 'outline'}
                    size="sm"
                    className={`min-w-[2rem] ${
                      currentPage === pageNum
                        ? isDarkMode
                          ? 'bg-green-600 hover:bg-green-700 text-white'
                          : 'bg-green-600 hover:bg-green-700 text-white'
                        : isDarkMode
                        ? 'border-slate-600 text-slate-300 hover:bg-slate-700'
                        : ''
                    }`}
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>

            <Button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              variant="outline"
              size="sm"
              className={isDarkMode ? 'border-slate-600 text-slate-300 hover:bg-slate-700' : ''}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RestaurantTable;
